"""
Takes a circuit (qasm file) and a physical topology and produces a hybrid 
logical-physical topology.
"""

from __future__ import annotations
from typing import Sequence
from re import I, S, match, findall
from pickle import load, dump
from networkx import Graph, shortest_path_length
from networkx.algorithms.traversal.breadth_first_search import descendants_at_distance

def check_multi(qasm_line):
	"""
	Determine if a line of QASM code is a multi-qubit interaction. If it is, 
	return a tuple of ints (control, target).
	"""
	if bool(match("cx", qasm_line)):
		# line is in the form - cx q[<control>], q[<target>];
		q = findall('\d+', qasm_line)
		return (int(q[0]), int(q[1]))
	else:
		return None


def add_logical_edge(
	physical_graph : Graph, 
	hybrid_graph : Graph, 
	a : int, 
	b : int, 
	options : dict[str]
	) -> Graph | None:
	"""
	Add a logical edge to either hybrid graph based off the options passed.

	Args:
		physical_graph (Graph): Graph of the physical topology.

		hybrid_graph (Graph): Graph of the hybrid topology.

		a (int): Primary vertex of edge.

		b (int): Secondary vertex of edge.

		options (dict[str]): 
			block_size (int): Defines the size of qudit groups

	Returns:
		updated_graph (Graph): Return the new hybird_graph.
	"""
	worst_dist = physical_graph.number_of_nodes()
	# TODO: edge_weight key may be wrong
	if shortest_path_length(hybrid_graph, a, b, weight="edge_weight"
		) > options["block_size"]-1:
		# Find all vertices that are blocksize-1 away from A
		candidates = descendants_at_distance(hybrid_graph, a, 
			options["block_size"] - 2)
		# Add an edge between the closest vertex from above and B
		best_dist = worst_dist
		best_node = a
		for node in candidates:
			dist = shortest_path_length(hybrid_graph, node, b)
			if dist < best_dist:
				best_dist = dist
				best_node = node
		hybrid_graph.add_edge(best_node, b, weight=best_dist)
	return hybrid_graph


def get_hybrid_edge_set(
	qasm_file : str, 
	coupling_file : str,
	options : dict[str]
) -> set[tuple[int]] | None:
	"""
	Given a qasm file and a physical topology, produce a hybrid topology where
	logical edges are added for unperformable gates.

	Args:
		qasm_file (str): Path to the qasm file specifying the circuit.

		coupling_file (str): Path to the coupling map specifying the topology.

		options (dict[str]): 
			block_size (int): Defines the size of qudit groups

	Returns:
		hybrid_edge_set (set[tuple[int]]): The physical topology with logical
			edges added for unperformable gates.
	"""
	if "block_size" not in options:
		print("block_size option missing")
		return None

	# Get the physical topology
	with open(coupling_file, 'rb') as f:
		physical_edge_set = load(f)
	# Add logical weights
	physical_edge_set = [(u,v,1) for (u,v) in physical_edge_set]
	
	# Convert the physical topology to a networkx graph
	hybrid_graph = Graph()
	physical_graph = Graph()
	hybrid_graph.add_edges_from(list(physical_edge_set))
	physical_graph.add_weighted_edges_from(list(physical_edge_set))

	# Get the logical connectivity graph
	logical_edge_list = []
	with open(qasm_file, 'r') as f:
		for qasm_line in f:
			if (edge := check_multi(qasm_line)) is not None:
				logical_edge_list.append(edge)

	# Add logical edges in order of path length
	for edge in logical_edge_list:
		rev_edge = (edge[1], edge[0])
		if rev_edge in logical_edge_list:
			logical_edge_list.remove(rev_edge)
	logical_edge_list = list(set(logical_edge_list))
	sorted(logical_edge_list, 
		key=lambda x: shortest_path_length(physical_graph, x[0], x[1])
	)

	for logical_edge in logical_edge_list:
		hybrid_graph = add_logical_edge(
			physical_graph, 
			hybrid_graph, 
			logical_edge[0],
			logical_edge[1],
			options
		)
	return set([edge for edge in hybrid_graph.edges])

def save_hybrid_topology(
	hybrid_graph : Sequence[Sequence[int]],
	qasm_file : str,
	coupling_file : str,
	options : dict[str]
) -> None:
	circ = qasm_file.split('qasm/')[-1].split('.qasm')[0]
	coup = coupling_file.split('coupling_maps/')[-1]
	size = str(options["block_size"])
	new_name = "hybrid_" + circ + "_" + coup + "_blocksize_" + size
	new_name += "_weighted"
	
	with open('coupling_maps/' + new_name, 'wb') as f:
		dump(hybrid_graph, f)
