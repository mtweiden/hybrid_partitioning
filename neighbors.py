from unicodedata import category
from bqskit import Circuit
from bqskit.ir.point import CircuitPoint
from bqskit.ir.gates.circuitgate import CircuitGate
import argparse
import pickle
import os
from itertools import permutations
from topology import construct_permuted_kernel, kernel_score_function


def calculate_overlap(group_a, group_b):
	"""
	Overlap is an integer that describes the number of pairs of qubits 
	in common a qubit group in the current layer has with any qubit groups
	in the previous layer. If there are multiple qubits in common bewtween 
	two blocks in a layer, edges inbetween those blocks should be kept.
	"""
	overlap = []
	for qubit in group_a:
		if qubit in group_b:
			overlap.append(qubit)
	return overlap


def get_induced_edges(edges, vertices):
	"""
	Return list of edges induced by vertices.
	"""
	induced_edges = []
	for a,b in edges:
		if a in vertices and b in vertices:
			induced_edges.append((a,b))
	return induced_edges


def relative_to_absolute_edges(qubit_group, relative_edges):
	absolute_edges = []
	for a,b in relative_edges:
		u = min(qubit_group[a], qubit_group[b])
		v = max(qubit_group[a], qubit_group[b])
		absolute_edges.append((u,v))
	return absolute_edges


def absolute_to_relative_edges(qubit_group, absolute_edges):
	absolute_qubits = set([])
	for u,v in absolute_edges:
		absolute_qubits.add(u)
		absolute_qubits.add(v)
	absolute_qubits = sorted(list(absolute_qubits))
	a2r_map = {a: qubit_group.index(a) for a in absolute_qubits}
	relative_edges = []
	for a,b in absolute_edges:
		u = min(a2r_map[a], a2r_map[b])
		v = max(a2r_map[a], a2r_map[b])
		relative_edges.append((u,v))
	return relative_edges


def combine_edge_sets(qubit_group, edges_a, edges_b):
	combined_edges = []
	for a,b in edges_a:
		if a in qubit_group and b in qubit_group:
			combined_edges.append((a,b))
	for a,b in edges_b:
		if a in qubit_group and b in qubit_group:
			combined_edges.append((a,b))
	return combined_edges


def load_subtopology_list(subtopology_dir):
	"""
	Get list of subtopology edges indexed by block number.
	"""
	subtopology_list = []
	file_list = [x for x in sorted(os.listdir(subtopology_dir)) if x.endswith('pickle')]
	for subtop_file in file_list:
		with open(f'{subtopology_dir}/{subtop_file}', 'rb') as f:
			subtopology_list.append(pickle.load(f))
	return subtopology_list


def get_block_logical_edges(circuit):
	"""
	Get list of logical connectivity edges indexed by block number.
	"""
	edge_list = []
	for op in circuit:
		if len(op.location) >= 2:
			edge_list.append(op.location)
	return edge_list


def get_templates(category, num_qubits):
	"""
	Valid template categories are:
		blocksize 3:
			lines, alls
		blocksize 4:
			lines, stars, rings, alls, embedded, trees
		blocksize 5:
			lines, stars, tees, dippers, alls, embedded, trees
	
	NOTE: embedded means embedded in a 2D nearest neighbor mesh
	"""

	line_2 = [(0,1)]
	line_3 = [(0,1), (1,2)]
	line_4 = [(0,1), (1,2), (2,3)]
	line_5 = [(0,1), (1,2), (2,3), (3,4)]
	alls_3 = [(0,1), (0,2), (1,2)]
	alls_4 = [(0,1), (0,2), (0,3), (1,2), (1,3), (2,3)]
	alls_5 = [(0,1), (0,2), (0,3), (0,4), (1,2), (1,3), (1,4), (2,3), (2,4), (3,4)]
	ring_4 = [(0,1), (1,2), (2,3), (0,3)]
	star_4 = [(0,1), (0,2), (0,3)]
	star_5 = [(0,1), (0,2), (0,3), (0,4)]
	dipper = [(0,1), (1,2), (2,3), (0,3), (0,4)]
	tees_5 = [(0,1), (1,2), (1,3), (3,4)]

	if num_qubits < 2:
		return []
	elif num_qubits == 2:
		return [line_2]
	elif num_qubits == 3:
		if category in ("lines", "stars", "rings", "embedded"):
			return [line_3]
		elif category == "alls":
			return [alls_3]
		else:
			raise RuntimeError(f"Unrecognized category {category}")
	elif num_qubits == 4:
		if category == "lines":
			return [line_4]
		elif category == "stars":
			return [star_4]
		elif category == "rings":
			return [ring_4]
		elif category == "alls":
			return [alls_4]
		elif category == "embedded":
			return [line_4, star_4, ring_4]
		elif category == "trees":
			return [line_4, star_4]
		else:
			raise RuntimeError(f"Unrecognized category {category}")
	elif num_qubits == 5:
		if category == "lines":
			return [line_5]
		elif category == "stars":
			return [star_5]
		elif category == "tees":
			return [tees_5]
		elif category == "dippers":
			return [tees_5]
		elif category == "alls":
			return [alls_5]
		elif category == "embedded":
			return [line_5, star_5, tees_5, dipper]
		elif category == "trees":
			return [line_5, star_5, tees_5]
		else:
			raise RuntimeError(f"Unrecognized category {category}")
	else:
		raise RuntimeError("Only upto 5 qubits blocks supported.")


def match_kernel(
	logical_ops, num_qubits, category
):
	"""
	Valid template categories are:
		blocksize 3:
			lines, alls
		blocksize 4:
			lines, stars, rings, alls, embedded, trees
		blocksize 5:
			lines, stars, tees, dippers, alls, embedded, trees
	
	NOTE: embedded means embedded in a 2D nearest neighbor mesh
	"""

	# handle the only 1-qubit gates case to avoid trying all options
	templates = get_templates(category, num_qubits)

	vertex_list  = list(range(num_qubits))
	vertex_perms = list(permutations(vertex_list, num_qubits))
	best_kernel = []
	best_score  = 0
	for template in templates:
		for perm in vertex_perms:
			permuted_kernel = construct_permuted_kernel(template, perm)
			edge_score, node_score = kernel_score_function(logical_ops, permuted_kernel)
			if edge_score > best_score:
				best_kernel = permuted_kernel
				best_score = edge_score

	return best_kernel


class debug_args():
	partitioned_circuit = "kernel_partitioning/partitioned_circuits/0a-add_17_mesh_25_blocksize_5_scan.pickle"
	subtopology_dir = "kernel_partitioning/subtopology_files/0a-add_17_mesh_25_blocksize_5_scan_kernel"

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("partitioned_circuit", type=str,
		default="partitioned_circuits/0a-add_17_mesh_25_blocksize_5_scan.pickle"
	) 
	parser.add_argument("subtopology_dir", type=str,
		default="subtopology_files/0a-add_17_mesh_25_blocksize_5_scan_kernel"
	) 
	parser.add_argument("valid_subtopologies", type=str, default="embedded") 
	args = parser.parse_args()

	# New subtopology directory name
	if not args.subtopology_dir.endswith('/'):
		curr_subtopologies = args.subtopology_dir
	else:
		curr_subtopologies = args.subtopology_dir[0:-1]
	new_subtopology_dir = f"subtopology_files/neighbors_{curr_subtopologies.split('/')[-1]}"
	if not os.path.exists(new_subtopology_dir):
		os.mkdir(new_subtopology_dir)

	with open(args.partitioned_circuit, "rb") as f:
		circuit = pickle.load(f)

	overlaps = []
	prev_groups = []
	prev_circuits = []
	circuit_structure = [[] for _ in range(circuit.num_cycles)]
	circuit_overlaps  = [[] for _ in range(circuit.num_cycles)]
	related_blocks = []
	logical_edges = []
	# Go though the circuit, look at the amount of overlap between adjacent cycle layers.
	# Assume that the subtopologies for the previous layer have been selected already. If
	# qubits that are present in the previous layer are present in the current layer, keep
	# any edges that exist between overlapping qubits. Otherwise select whichever subtopology
	# is most similiar to the logical connectivity of the block.
	blocks_seen = 0
	for cycle in range(circuit.num_cycles):
		groups = []
		circuits = []
		for qubit in range(circuit.num_qudits):
			try:
				new_op = circuit.get_operation(CircuitPoint(cycle,qubit))
				if new_op.location not in groups and isinstance(new_op.gate, CircuitGate):
					dummy_circ = Circuit(len(new_op.location))
					dummy_circ.append_gate(
						new_op.gate, range(len(new_op.location)), new_op.params
					)
					dummy_circ.unfold_all()
					logical_edges.append(get_block_logical_edges(dummy_circ))
					groups.append(new_op.location)
					# New entry for each block
					related_blocks.append([])
			except IndexError:
				continue

		overlaps = [[] for _ in range(len(groups))]
		if len(prev_groups) > 0:
			for block_index, g in enumerate(groups):
				for prev_index, pg in enumerate(prev_groups):
					curr_overlap = calculate_overlap(g, pg)
					# Only care about cases where there is more than 1 qubit of overlap
					if len(curr_overlap) > 1:
						overlaps[block_index].extend(curr_overlap)
						related_blocks[blocks_seen + block_index].append(
							blocks_seen - len(prev_groups) + prev_index
						)
						related_blocks[blocks_seen - len(prev_groups) + prev_index].append(
							blocks_seen + block_index
						)
					
		# Update state
		circuit_structure[cycle] = groups
		circuit_overlaps[cycle] = overlaps
		# Add overlaps to the previous cycle too
		if cycle > 0:
			# Look at overlapping qubits in the current layer. If they in a block in the
			# previous layer, and them to the overlapping qubits for that block in the
			# previous layer.
			for curr_block_offset, _ in enumerate(circuit_structure[cycle]):
				for prev_block_offset, prev_block_qubits in enumerate(circuit_structure[cycle - 1]):
					for cq in overlaps[curr_block_offset]:
						if cq in prev_block_qubits:
							if cq not in circuit_overlaps[cycle-1][prev_block_offset]:
								circuit_overlaps[cycle-1][prev_block_offset].append(cq)
		prev_groups = groups
		prev_circuits = circuits
		blocks_seen += len(groups)

	# NOTE: Overlap means that that qubit is involved in either the forward or backward 
	# neighboring block as well. Keeping edges between verticies with overlap may result
	# in less routing needed.
	# Translate overlap lists into relative numbering within some qubit group
	cycle_count = 0
	block_count = 0
	flat_relative_overlap = []
	flat_circuit_structure = []
	# Go through cycle
	for cycle, cycle_structure in enumerate(circuit_structure):
		## Each block in cycle
		#print(f"cycle_structure: {cycle_structure}")
		#print(f"cycle overlap: {circuit_overlaps[cycle]}")
		for block, block_structure in enumerate(cycle_structure):
			block_count += 1
			relative_overlap = []
			overlaps = circuit_overlaps[cycle]
			# Each qubit in block
			for index, qubit in enumerate(sorted(block_structure)):
				for lap in overlaps:
					if qubit in lap:
						relative_overlap.append(index)
			flat_relative_overlap.append(relative_overlap)
			flat_circuit_structure.append(sorted(block_structure))
	#print(flat_relative_overlap)
	
	# flat_relative_structure has vertices of which we want induced subgraphs for
	# for each block. Take structure of circuit (list of groups where index is
	# the block number), and access the two lists in parallel. Also need a list
	# of the subtopologies in the circuit that can be accessed in the same way.
	subtopology_list = load_subtopology_list(args.subtopology_dir)
	if len(subtopology_list) != block_count:
		raise RuntimeError(
			f"Subtopology list length ({len(subtopology_list)})"
			f"is not equal to block count ({block_count})"
		)

	# Go through each block
	shared_logical_edges = []
	for block_num in range(block_count):
		shared_logical_edges.append(
			get_induced_edges(
				list(set(logical_edges[block_num])),
				flat_relative_overlap[block_num]
			)
		)
	#print(shared_logical_edges)
	#print(len(shared_logical_edges))

	#for block_num, related in enumerate(related_blocks):
	#	print(f'block {block_num} related to {related}')
	#	print(f'{block_num} - {flat_circuit_structure[block_num]}')
	#	for r in related:
	#		print(f'\t{r} - {flat_circuit_structure[r]}')
	
	#print(shared_logical_edges)

	# Suggested edges are edges that are shared between neighboring blocks and 
	# are in the logical connectivity graph of the current block. Try picking a
	# subtopology from these edges first, then if there are not enough edges, add
	# the next most used edge in the logical connectivity graph such that we still
	# end up with a 
	for block_num in range(block_count):
		# Weight the selection of shared edges by counting how many time the edges are
		# used in neighboring blocks.
		absolute_current_edges = relative_to_absolute_edges(
			flat_circuit_structure[block_num],
			logical_edges[block_num]
		)

		absolute_related_edges = []
		for related_block_num in related_blocks[block_num]:
			absolute_related_edges += relative_to_absolute_edges(
				flat_circuit_structure[related_block_num],
				logical_edges[related_block_num]
			)
		combined_edge_set = combine_edge_sets(
			flat_circuit_structure[block_num],
			absolute_current_edges,
			absolute_related_edges,
		)
		relative_combined_edge_set = absolute_to_relative_edges(
			flat_circuit_structure[block_num],
			combined_edge_set
		)
		#print(relative_combined_edge_set)
		best_subtopology = match_kernel(
			relative_combined_edge_set,
			len(flat_circuit_structure[block_num]), 
			args.valid_subtopologies
		)
		print(best_subtopology)

		from math import log10, ceil
		block_num_str = str(block_num).zfill(ceil(log10(block_count)))
		block_name = f"block_{block_num_str}_kernel.pickle"
		with open(f"{new_subtopology_dir}/{block_name}", "wb") as f:
			pickle.dump(best_subtopology, f)

	with open(f"{new_subtopology_dir}/structure.pickle", "wb") as f:
		pickle.dump(flat_circuit_structure, f)
