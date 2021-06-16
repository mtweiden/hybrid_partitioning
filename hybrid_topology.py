"""
Takes a circuit (qasm file) and a physical topology and produces a hybrid 
logical-physical topology.
"""

from __future__ import annotations
from typing import Sequence
from re import S, match, findall
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
			reuse_edges (bool): If True, check hybrid graph for vertex dist-
				ances. If False, use physical graph for vertex distances.
			shortest_path (bool): If True, find the physicall closest vertex. If
				False, use the vertices directly.

	Returns:
		updated_graph (Graph): Return the new hybird_graph.
	"""
	worst_dist = physical_graph.number_of_nodes()
	if options["reuse_edges"]:
		if shortest_path_length(hybrid_graph, a, b) > options["block_size"]-1:
			if options["shortest_path"]:
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
				hybrid_graph.add_edge(best_node, b)
			else:
				hybrid_graph.add_edge(a, b)
	else:
		if shortest_path_length(physical_graph, a, b) > options["block_size"]-1:
			if options["shortest_path"]:
				# Find all vertices that are blocksize-1 away from A
				candidates = descendants_at_distance(physical_graph, a, 
					options["block_size"] - 2)
				# Add an edge between the closest vertex from above and B
				best_dist = worst_dist
				best_node = a
				for node in candidates:
					dist = shortest_path_length(physical_graph, node, b)
					if dist < best_dist:
						best_dist = dist
						best_node = node
				hybrid_graph.add_edge(best_node, b)
			else:
				hybrid_graph.add_edge(a, b)
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
			reuse_edges (bool): If True, check hybrid graph for vertex dist-
				ances. If False, use physical graph for vertex distances.
			shortest_path (bool): If True, find the physicall closest vertex. If
				False, use the vertices directly.

	Returns:
		hybrid_edge_set (set[tuple[int]]): The physical topology with logical
			edges added for unperformable gates.
	"""
	if "block_size" not in options:
		print("block_size option missing")
		return None
	if "reuse_edges" not in options:
		print("reuse_edges option missing")
		return None
	if "shortest_path" not in options:
		print("shortest_path option missing")
		return None
	if "add_interactors" not in options:
		print("add_interactors option missing")
		return None

	# Get the logical connectivity graph
	logical_edge_list = []
	with open(qasm_file, 'r') as f:
		for qasm_line in f:
			if (edge := check_multi(qasm_line)) is not None:
				logical_edge_list.append(edge)

	for edge in logical_edge_list:
		rev_edge = (edge[1], edge[0])
		if rev_edge in logical_edge_list:
			logical_edge_list.remove(rev_edge)
			logical_edge_list.append(edge)
	edge_ranks = {edge:0 for edge in logical_edge_list}
	for edge in logical_edge_list:
		edge_ranks[edge] += 1
	logical_edge_list = list(set(logical_edge_list))

	sorted(logical_edge_list, key=lambda x: edge_ranks[x])

	# Get the physical topology
	with open(coupling_file, 'rb') as f:
		physical_edge_set = load(f)
	
	# Convert the physical topology to a networkx graph
	hybrid_graph = Graph()
	physical_graph = Graph()
	hybrid_graph.add_edges_from(list(physical_edge_set))
	physical_graph.add_edges_from(list(physical_edge_set))

	worst_dist = physical_graph.number_of_nodes()
	ledger = [[0 for y in range(worst_dist)] for x in range(worst_dist)]
	for logical_edge in logical_edge_list:
		a = logical_edge[0]
		b = logical_edge[1]
		hybrid_graph = add_logical_edge(physical_graph, hybrid_graph, a, b, 
			options)
		if options["add_interactors"]:
			for other_node in range(worst_dist):
				ledger[a][other_node] += 1
				ledger[b][other_node] += 1
				if ledger[a][other_node] >= 3:
					hybrid_graph = add_logical_edge(
						physical_graph, hybrid_graph, b, other_node, options
					)
				if ledger[b][other_node] >= 3:
					hybrid_graph = add_logical_edge(
						physical_graph, hybrid_graph, a, other_node, options
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
	if options["reuse_edges"]:
		new_name += "_reuseedges"
	if options["shortest_path"]:
		new_name += "_shortestpath"
	if options["add_interactors"]:
		new_name += "_addinteractors"
	
	with open('coupling_maps/' + new_name, 'wb') as f:
		dump(hybrid_graph, f)
