"""
Takes a circuit (qasm file) and a physical topology and produces a hybrid 
logical-physical topology.
"""

from __future__ import annotations
from collections import UserString
import pickle
from typing import OrderedDict, Sequence
from re import match, findall
from pickle import load, dump
from networkx import Graph, shortest_path_length
import networkx
from networkx.algorithms.shortest_paths.generic import shortest_path
from networkx.algorithms.traversal.breadth_first_search import descendants_at_distance
from itertools import combinations
from bqskit import Circuit

from networkx.classes.function import neighbors, subgraph

def check_multi(qasm_line):
	"""
	Determine if a line of QASM code is a multi-qubit interaction. If it is, 
	return a tuple of ints (control, target).
	"""
	if bool(match("cx", qasm_line)) or bool(match("swap", qasm_line)):
		# line is in the form - cx q[<control>], q[<target>];
		q = findall('\d+', qasm_line)
		return (int(q[0]), int(q[1]))
	else:
		return None


def get_logical_operations(
	circuit: Circuit,
	qudit_group: Sequence[int] | None = None,
) -> Sequence[Sequence[int]]:
	logical_operations = []
	for op in circuit:
		if len(op.location) > 1:
			for edge in combinations(op.location, 2):
				logical_operations.append(edge)
	if qudit_group is not None:
		logical_operations = [(qudit_group[op[0]], qudit_group[op[1]]) 
			for op in logical_operations]
	return logical_operations


def is_partitionable(
	physical_topology: Graph,
	qudit_group: Sequence[int],
	edge: tuple[int]
) -> bool:
	subgraph = physical_topology.subgraph(qudit_group)
	try:
		return shortest_path_length(subgraph,edge[0],edge[1]) < len(qudit_group)
	except networkx.exception.NetworkXNoPath:
		return False


def get_unpartitionable_edges(
	logical_operations : Sequence[Sequence[int]],
	physical_topology : Graph,
	qudit_group : Sequence[int],
) -> Sequence[Sequence[int]]:
	"""
	Gates that require a logical edge to be inserted into the hybrid topology.
	"""
	return [
		edge for edge in logical_operations if not 
		is_partitionable(physical_topology, qudit_group, edge)
	]


def get_partitionable_edges(
	logical_operations : Sequence[Sequence[int]],
	physical_topology : Graph,
	qudit_group : Sequence[int],
) -> Sequence[Sequence[int]]:
	"""
	Gates that can be implemented on physical edges but non adjacent vertices.
	"""
	physical = get_physical_edges(logical_operations, physical_topology)
	partitionable = [
		edge for edge in logical_operations if 
		is_partitionable(physical_topology, qudit_group, edge)
	]
	non_physical = [
		(u,v) for (u,v) in partitionable if 
		(u,v) not in physical and (v,u) not in physical
	]
	return non_physical


def get_physical_edges(
	logical_operations : Sequence[Sequence[int]],
	physical_topology : Graph,
) -> Sequence[Sequence[int]]:
	"""
	Gates that correspond directly to edges in the physical topology.
	"""
	return [
		(u,v) for (u,v) in logical_operations if (u,v) in 
		physical_topology.edges or (v,u) in physical_topology.edges
	]


def estimate_cnot_count(
	operations : Sequence[Sequence[int]],
	hybrid_topology : Graph,
	qudit_group : Sequence[int] | None = None,
) -> int:
	est = 0
	if qudit_group is None:
		for (u,v) in operations:
			est += shortest_path_length(hybrid_topology, u, v) + 1
	else:
		subgraph = hybrid_topology.subgraph(qudit_group)
		for (u,v) in operations:
			est += shortest_path_length(subgraph, u, v, weight="weight") + 1
	return est


def cost_function(distance: int) -> int:
	"""
	Give the cost of a path in the physical topology.

	Args:
		distance (int): Distance in the physical topology.

	Returns:
		cost (int): The result of the cost function. 
	"""
	# Number of CNOTs needed to SWAP two qudits along the same path
	#return 3 * (2 * distance - 1)
	# Cost function: The number of CNOTs needed to perform a single logical
	# CNOT operation then restore the pre-operation layout of the circuit.
	#return 3 * 2 * (distance - 1) + 1
	# Number of CNOTs needed to get Qubits in range for CNOT and SWAP back
	#return 3 * 2 * (distance - 1)
	# Number of CNOTs needed to SWAP
	return 3 * 2 * (distance)


def add_logical_edges(
	physical_topology : Graph,
	hybrid_topology : Graph,
	qudit_group : Sequence[int],
	logical_edge_list : Sequence[Sequence[int]],
	options : dict[str],
) -> Graph:
	"""
	Add a logical edge to either hybrid graph based off the options passed.

	Args:
		physical_graph (Graph): Graph of the physical topology.

		hybrid_graph (Graph): Graph of the hybrid topology.

		logical_edge (tuple[int]): A weighted logical edge.		

		options (dict[str]): 
			nearest_physical (bool): Add logical edges between members of the
				qudit_group. Considers the two separate possibly disjoint 
				connected components containing vertex_a and vertex_b, and 
				finds the shortest path between these two sets.

			nearest_logical (bool): Adds logical edges between members of
				the qudit_group. The edge is added so that both vertex_a and 
				vertex_b are connected to their nearest neighbors that are also
				in the qudit_group. If the qudit group is still unconnected,
				the shortest distance logical edges will be added until the 
				whole qudit_group is connected.
			
			shortest_direct (bool): Connect vertices as end points using the
				shortest direct path in the physical topology (default).
		
		qudit_group (Sequence[int]): If provided, only qudit_group members will
			be used as end points of logical edges.

	Returns:
		updated_graph (Graph): Return the new hybird_graph.
	"""
	hybrid_graph = hybrid_topology.copy()
	unpartitionable_edges = get_unpartitionable_edges(logical_edge_list, 
		physical_topology, qudit_group)
	if options["nearest_physical"]:
		# Shortest path between vertices physically connected to vertex_a and
		# vertices physically connected to vertex_b
		subgraph = physical_topology.subgraph(qudit_group)
		for (vertex_a, vertex_b, _) in unpartitionable_edges:
			candidates_a = list(shortest_path(subgraph, vertex_a).keys())
			candidates_b = list(shortest_path(subgraph, vertex_b).keys())
			best_dist = physical_topology.number_of_nodes()
			best_node_a = vertex_a
			best_node_b = vertex_b
			for a in candidates_a:
				for b in candidates_b:
					dist = shortest_path_length(physical_topology, a, b)
					if dist < best_dist and dist > 0:
						best_dist = dist
						best_node_a = a
						best_node_b = b
			hybrid_graph.add_edge(best_node_a, best_node_b,
				weight=cost_function(best_dist))

	elif options["nearest_logical"]:
		subgraph = physical_topology.subgraph(qudit_group)
		# Find all disconected subgroups, add the closest
		reachable = list(shortest_path(subgraph, qudit_group[0]).keys())
		# While there are still disconnected subgroups
		while len(reachable) < len(qudit_group):
			# Find the edge that connects two disjoint subgroups with the
			# minimum cost and add it to the subgraph
			best_dist = physical_topology.number_of_nodes()
			unreachable = list(set(qudit_group) - set(reachable))
			best_qudit = qudit_group[0]
			best_other = unreachable[0]
			for qudit in qudit_group:
				for other in unreachable:
					dist = shortest_path_length(physical_topology, qudit, other)
					if dist < best_dist and dist > 0:
						best_dist = dist
						best_qudit = qudit
						best_other = other
			hybrid_graph.add_edge(best_qudit, best_other, 
				weight=cost_function(best_dist))
			reachable = list(shortest_path(subgraph, qudit_group[0]).keys())

	else: # shortest_direct assumed
		for (vertex_a, vertex_b, distance) in unpartitionable_edges:
			hybrid_graph.add_edge(vertex_a, vertex_b, 
				weight=cost_function(distance))

	return hybrid_graph


def get_hybrid_edge_set(
	circuit_file : str, 
	coupling_file : str,
	qudit_group : Sequence[int],
	options : dict[str],
) -> set[tuple[int]] | None:
	"""
	Given a qasm file and a physical topology, produce a hybrid topology where
	logical edges are added for unperformable gates.

	Args:
		circuit_file (str): Path to the file specifying the circuit.

		coupling_file (str): Path to the coupling map specifying the topology.

		qudit_group (Sequence[int]): Only qudit_group members will be used as
			end points of logical edges.

		options (dict[str]): 
			block_size (int): Defines the size of qudit groups
			is_qasm (bool): Whether the circuit_file is qasm or pickle.

	Returns:
		hybrid_edge_set (set[tuple[int]]): The physical topology with logical
			edges added for unpartitionable gates.
	
	Raises:
		ValueError: If `block_size` key is not in `options`.
	"""
	if "block_size" not in options:
		raise ValueError("The `block_size` entry in	`options` is required.")

	# Get the physical topology
	with open(coupling_file, 'rb') as f:
		physical_edge_set = load(f)
	# Add logical weights
	physical_edge_set = [(u,v,1) for (u,v) in physical_edge_set]
	
	# Convert the physical topology to a networkx graph
	physical_graph = Graph()
	physical_graph.add_weighted_edges_from(list(physical_edge_set))
	# Build the hybrid topology starting with physical edges
	hybrid_graph = physical_graph.subgraph(qudit_group)

	# Get the logical connectivity graph
	logical_operations = []
	# QASM format
	if options['is_qasm']:
		with open(circuit_file, 'r') as f:
			for qasm_line in f:
				if (edge := check_multi(qasm_line)) is not None:
					logical_operations.append(edge)
	# Pickle format
	else:
		with open(circuit_file, 'rb') as f:
			circuit = pickle.load(f)
		logical_operations = get_logical_operations(circuit, qudit_group)
			
	# Sort logical edges by edge frequency
	# TODO: Sort logical edges in order of path length
	for edge in logical_operations:
		rev_edge = (edge[1], edge[0])
		if rev_edge in logical_operations:
			logical_operations.remove(rev_edge)
			logical_operations.append(edge)
	logical_operations = sorted(logical_operations,
		key=logical_operations.count, reverse=True)
	logical_operations = list(OrderedDict.fromkeys(logical_operations))
	logical_edge_list = [
		(e[0], e[1], shortest_path_length(physical_graph, e[0], e[1])) for
			e in logical_operations
	]

	# Add edges to graph
	hybrid_graph = add_logical_edges(
		physical_graph,
		hybrid_graph,
		qudit_group,
		logical_edge_list,
		options
	)
	hybrid_graph.add_weighted_edges_from(physical_edge_set)

	hybrid_edge_set = set([
		(u,v, hybrid_graph[u][v]["weight"]) for (u,v) in hybrid_graph.edges
	])
	physical = get_physical_edges(logical_operations, physical_graph)
	partitionable = get_partitionable_edges(logical_operations,
		physical_graph, qudit_group)
	unpartitionable = get_unpartitionable_edges(logical_operations,
		physical_graph, qudit_group)

	physical_cost = estimate_cnot_count(physical, hybrid_graph)
	partitionable_cost = estimate_cnot_count(partitionable, hybrid_graph, 
		qudit_group)
	unpartitionable_cost = estimate_cnot_count(unpartitionable, hybrid_graph, 
		qudit_group)
	total_cost = sum([physical_cost, partitionable_cost, unpartitionable_cost])

	print(f"Qudit group: {qudit_group}")
	print(f"  Number of physical operations: {len(physical)}")
	print(f"    Estimated physical CNOT count: {physical_cost}")
	print(f"  Number of partitionable operations: {len(partitionable)}")
	print(f"    Estimated partitionable CNOT count: {partitionable_cost}")
	print(f"  Number of unpartitionable operations: {len(unpartitionable)}")
	print(f"    Estimated unpartitionable CNOT count: {unpartitionable_cost}")
	print(f"  Estimated total CNOT count: {total_cost}")
	print()
	return hybrid_edge_set

