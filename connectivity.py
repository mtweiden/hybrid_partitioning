from __future__ import annotations
from pickle import load, dump
from typing import Sequence

import networkx as nx
import re
import argparse
from os import listdir
import gc

from bqskit import Circuit
from bqskit.ir.lang.qasm2.qasm2 import OPENQASM2Language
from bqskit.ir.gates.constant.cx import CNOTGate
from bqskit.ir.gates.parameterized.u3 import U3Gate

# Take as input a Sequence[Sequence[int]]
# Create a networkx graph
# Get the 2nd eigenvalue of the Laplacian
# Get the modularity or Q-value
# Get the graph expansion

class Connectivity:

	def __init__(
		self, 
		qasm_file : str, 
		subtopology_file : str,
		synthesized_file : str | None,
	):
		"""
		Given a QASM file, create a logical connectivity graph using the
		networkx Graph class.

		Arguments:
			qasm_file (str): Quantum subcircuit for which the logical
				connectivity graph will be generated.

			subtopology_file (str): Synthesis subtopology for the block associated
				with qasm_file.

			synthesized_file (str): Synthesized version of qasm_file. 
		"""
		# Convert qasm file to a list of edges
		self.edge_list = self._parse_qasm_file(qasm_file)
		#edges = list(set(self.edge_list.copy()))
		#self.weights = {x: self.edge_list.count(x) for x in edges}

		# Create networkx graph
		self.logical_graph = nx.Graph()
		for (u,v) in self.edge_list:
			#self.logical_graph.add_edge(u,v,weight=self.weights[(u,v)])
			self.logical_graph.add_edge(u,v)
		
		# Load the subtopology if it exists, it should be in pickle format
		with open(subtopology_file, "rb") as f:
			subtopology_edges = load(f)
		self.subtopology_graph = nx.Graph()
		for (s,t) in subtopology_edges:
			self.subtopology_graph.add_edge(s,t)

		# Create bqskit circuit
		with open(qasm_file, "r") as f:
			self.circuit = OPENQASM2Language().decode(f.read())

		self.synth_circuit = None
		# Get synthesized circuit as well if provided
		if synthesized_file is not None:
			with open(synthesized_file, "r") as f:
				self.synth_circuit = OPENQASM2Language().decode(f.read())


	def _parse_qasm_file(
		self, 
		qasm_file : str
	) -> Sequence[Sequence[int]]:
		# Open the file
		edges = []
		# All blocks should be in the CX and U3 gate set
		with open(qasm_file, "r") as f:
			# Check each multi
			for line in f:
				if re.match(r"cx", line):
					(a,b) = re.findall(r"\d+", line)
					edges.append((a,b))
					#self.cnots += 1
				#elif re.match(r"u3", line):
					#self.u3s += 1
		return edges


	def measure(self) -> Sequence[float,float]:
		width = self.circuit.num_qudits
		depth = self.circuit.depth
		log_edges = 0
		log_eig   = 0
		synth_edges = 0
		synth_eig   = 0
		cnots = 0
		u3s   = 0
		synth_cnots = 0
		synth_u3s   = 0

		if U3Gate() in self.circuit.gate_set:
			u3s = self.circuit.count(U3Gate())
		if CNOTGate() in self.circuit.gate_set:
			cnots = self.circuit.count(CNOTGate())

		if self.synth_circuit is not None:
			if U3Gate() in self.synth_circuit.gate_set:
				synth_u3s = self.synth_circuit.count(U3Gate())
			if CNOTGate() in self.synth_circuit.gate_set:
				synth_cnots = self.synth_circuit.count(CNOTGate())

		if len(self.logical_graph.nodes) > 0:
			log_edges = len(self.logical_graph.edges)
			log_eig = nx.algebraic_connectivity(self.logical_graph, normalized=True)
			synth_edges = len(self.subtopology_graph.edges)
			synth_eig = nx.algebraic_connectivity(self.subtopology_graph, normalized=True)

		return (
			width, 
			depth,
			cnots,
			u3s,
			synth_cnots,
			synth_u3s,
			log_edges,
			log_eig,
			synth_edges,
			synth_eig,
		)


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("partition_dir", type=str)
	parser.add_argument("subtopology_dir", type=str)
	parser.add_argument("synthesis_dir", type=str)
	args = parser.parse_args()

	block_list = sorted(listdir(args.partition_dir))
	block_list.remove("structure.pickle")
	subtopology_list = sorted(listdir(args.subtopology_dir))
	subtopology_list.remove("summary.txt")
	synthesis_list = sorted([x for x in listdir(args.synthesis_dir) if x.endswith(".qasm")])

	if len(block_list) != len(subtopology_list):
		raise RuntimeError(
			f"Unequal number of block and subtopology files!"
		)
	
	output_name = f"{args.partition_dir.split('/')[-1]}.pickle"
	if output_name == ".pickle":
		output_name = f"{args.partition_dir.split('/')[-2]}.pickle"

	stat_list = []
	for block_num in range(len(block_list)):
		block_name = block_list[block_num]
		subtopology_name = subtopology_list[block_num]
		analyzer = Connectivity(
			f"{args.partition_dir}/{block_name}",
			f"{args.subtopology_dir}/{subtopology_name}",
			f"{args.synthesis_dir}/{block_name}",
		)
		stat_list.append(analyzer.measure())
		del analyzer
		gc.collect()

	from pprint import pprint
	pprint(stat_list)
	# CHECK THAT STAT_LIST IS PROPERLY FORMATTED

	with open(f"stats/{output_name}", "wb") as f:
		dump(stat_list, f)
