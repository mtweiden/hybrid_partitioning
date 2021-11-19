from __future__ import annotations
from typing import Any, Sequence

from statistics import mean

from bqskit.ir.operation import Operation
from topology import get_logical_operations
from bqskit import Circuit
from bqskit.ir.lang.qasm2.qasm2 import OPENQASM2Language
from bqskit.ir.gates.constant.swap import SwapGate
from bqskit.ir.gates.constant.cx import CNOTGate

class PartitionRecord():
	"""
	A list of these makes up an analyzer. Record things like
		- current operations
		- touches per qubit
		- partition start cycle
		- partition stop cycle
		- hops/locations by each qubit during partition
		- swaps during partition
	"""
	def __init__(
		self,
		qubit_group : Sequence[int],
		block_file : str,
	):
		self.qubit_group = qubit_group
		with open(block_file, "r") as f:
			circ = OPENQASM2Language().decode(f.read())
		self.unseen_operations = get_logical_operations(circ, qubit_group)
		self.seen_operations   = []

		self.touches = {q:0 for q in qubit_group}
		self.travel  = {q:[] for q in qubit_group}
		self.start_cycle = -1
		self.stop_cycle = -1
		self.swaps = 0
		self.cnots = 0

	def is_partition_started(self) -> bool:
		return len(self.seen_operations) > 0
	
	def is_partition_finished(self) -> bool:
		return len(self.unseen_operations) == 0
	
	def is_partition_active(self) -> bool:
		return self.is_partition_started() and not self.is_partition_finished()
	
	def analyze_swap(
		self, 
		logical_numbers : Sequence[int], 
		physical_numbers : Sequence[int],
	) -> bool:
		"""
		If SWAP is in this partition, update:
			- number of internal swaps
			- travel dictionary
			- touches dictionary
		"""
		if not self.is_partition_active():
			return False
		active_qubits = [q for q in self.qubit_group if self.touches[q] > 0]
		# Check if any active qubits were touched by this swap
		memberships = [
			q in logical_numbers and q in active_qubits for q in self.qubit_group
		]
		# If it touched any qubit in the partition, add to internals
		if member_status := any(memberships):
			self.swaps += sum(memberships) / 2
			# Update the travel and touches dictionaries
			for index in range(2):
				# Retest membership
				if logical_numbers[index] in self.qubit_group:
					self.travel[logical_numbers[index]].append(physical_numbers[index])
					self.touches[logical_numbers[index]] += 1
		return member_status


	def match_operands(
		self,
		operands : Sequence[int],
	) -> int:
		"""
		Codes:
			0 - no operands match
			1 - one operand matches
			2 - both operands match
		"""
		# Go through logical operations, try to match with the operands
		for block_operands in self.unseen_operations:
			u = min(operands)
			v = max(operands)
			a = min(block_operands)
			b = max(block_operands)
			match = sum([u == a, v == b])
			if match > 0:
				return match # Should always return 2
		return 0

	
	def analyze_cnot(
		self, 
		logical_numbers : Sequence[int],
		p2l_mapping     : dict[int,int],
		cycle : int,
	) -> bool:
		"""
		If CNOT is in this partition
			- seen operations
			- touches dictionary
			- start cycle if not started
			- stop cycle
		"""
		# If not yet finished,
		if self.is_partition_finished():
			return False
		# Check the first to see if the operands match
		match_code = self.match_operands(logical_numbers)

		if match_code == 0:
			return False
		elif match_code == 1:
			raise RuntimeError(
				f"Got a partial match of operands!\n"
				f"logical: {logical_numbers} - qubit group: {self.qubit_group}"
			)
		else: # Both operands match
			if not self.is_partition_started():
				# Update start
				self.start_cycle = cycle
				# Get logical to physical mapping for group
				# This results in over counting, only add location of actives
			
			# Check if this is the first time a qudit has been used in block
			activated_qubits = [
				q in logical_numbers and self.touches[q] == 0 
				for q in self.qubit_group
			]
			# Add locaiton to activated qubits
			if any(activated_qubits):
				l2p_mapping = {
					l:p for p,l in p2l_mapping.items() if l in self.qubit_group
				}
				for index in range(len(self.qubit_group)):
					if activated_qubits[index]:
						self.travel[self.qubit_group[index]].append(
							l2p_mapping[self.qubit_group[index]]
						)
			
			if not self.is_partition_finished():
				# Update stop
				self.stop_cycle  = cycle
				# Update touches
				for qubit in logical_numbers:
					self.touches[qubit] += 1
				# Update seen/unseen
				(a,b) = logical_numbers
				if (a,b) in self.unseen_operations:
					self.unseen_operations.remove((a,b))
					self.seen_operations.append((a,b))
				else: # Should never happen, but just in case
					self.unseen_operations.remove((b,a))
					self.seen_operations.append((b,a))
				self.cnots += 1

			return True

class PartitionAnalyzer():
	def __init__(
		self, 
		mapped_circuit_file : str,
		block_dir           : str,
		block_list     : Sequence[str],
		structure_list : Sequence[Sequence[int]],
		num_physical_qubits : int,
	):
		self.circuit_file : str  = mapped_circuit_file
		self.block_dir    : str  = block_dir
		self.block_list   : Sequence[Sequence[int]] = block_list 

		self.record_list : Sequence[PartitionRecord] = []
		for block_num in range(len(self.block_list)):
			self.record_list.append(
				PartitionRecord(
					structure_list[block_num],
					f"{block_dir}/{block_list[block_num]}",
				)
			)
		self.cnots = 0
		self.swaps = 0
		self.earliest_unfinished = 0
		self.active_blocks = []
		self.p2l_mapping = {k:k for k in range(num_physical_qubits)}
	
	def analyze_operation(
		self, 
		op : Operation, 
		cycle : int
	) -> None | tuple[int, int]:
		# Check if it is multi qubit
		if len(operands := op.location) <= 1:
			return None

		#print(f"operation [{op.gate.qasm_name}]: {op.location}")

		# Translate the from physical to logical qubits
		logical_qubits = (
			self.p2l_mapping[operands[0]], self.p2l_mapping[operands[1]]
		)
		physical_qubits = operands

		if isinstance(op.gate, SwapGate):
			# Count all swaps
			self.swaps += 1
			# Update physical to logical mapping
			self.p2l_mapping[physical_qubits[0]] = logical_qubits[1]
			self.p2l_mapping[physical_qubits[1]] = logical_qubits[0]

			# Update the qubit locations and touches for active blocks
			now_finished = []
			for block_num in self.active_blocks:
				if self.record_list[block_num].is_partition_finished():
					now_finished.append(block_num)
			# Update active blocks
			self.active_blocks = [
				b for b in self.active_blocks if not b in now_finished
			]
			match = 0
			for block_num in self.active_blocks:
				# Record no longer active blocks
				match += self.record_list[block_num].analyze_swap(
					logical_qubits,
					physical_qubits,
				)
				if match >= 1:
					break

		elif isinstance(op.gate, CNOTGate):
			# Count all cnots
			self.cnots += 1

			# Find the earliest unfinished block
			while self.record_list[self.earliest_unfinished].is_partition_finished():
				self.earliest_unfinished += 1

			# Find find the first unfinished block that has this interaction
			for block_num in range(self.earliest_unfinished, len(self.block_list)):
				#print(f"Block number: {block_num}")
				#print(f"Group: {self.record_list[block_num].qubit_group}")
				match = self.record_list[block_num].analyze_cnot(
					logical_qubits, 
					self.p2l_mapping,
					cycle
				)
				if match:
					if block_num not in self.active_blocks:
						self.active_blocks.append(block_num)
					break
	
	def run(self):
		# Open file
		with open(self.circuit_file, "r") as f:
			circuit = OPENQASM2Language().decode(f.read())

		# Iterate through circuit, see which 
		for cycle, op in circuit.operations_with_cycles():
			self.analyze_operation(op, cycle)

		average_touches = []
		average_distances = []
		total_distances = []
		total_touches = []
		durations = []
		internal_swaps = []
		for record in self.record_list:
			touches = list(record.touches.values())
			total_touch = 0
			for t in touches:
				total_touch += t
			total_touches.append(total_touch)
			average_touches.append(total_touch/len(record.qubit_group))
			distances = list(record.travel.values())
			total_distance = 0
			for d in distances:
				total_distance += max(len(d) - 1, 0)
			total_distances.append(total_distance)
			average_distances.append(total_distance/len(record.qubit_group))
			durations.append(record.stop_cycle - record.stop_cycle)
			internal_swaps.append(record.swaps)
		
		for block_num in range(len(self.record_list)):
			string = f"BLOCK {block_num}\n"
			#string += f"  total distance: {total_distances[block_num]}\n"
			string += f"  average distance: {average_distances[block_num]}\n"
			#string += f"  total touches: {total_touches[block_num]}\n"
			string += f"  average touches:  {average_touches[block_num]}\n"
			string += f"  duration:         {durations[block_num]}\n"
			string += f"  swaps:            {internal_swaps[block_num]}\n"
			print(string)

		print("Total CNOTS: ", self.cnots)
		print("Total SWAPS: ", self.swaps)
		print("  Internal SWAPs ", sum(internal_swaps))