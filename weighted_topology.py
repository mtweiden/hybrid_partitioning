"""
Takes a circuit (qasm file) and a physical topology and produces a hybrid 
logical-physical topology.
"""

from __future__ import annotations
import pickle
from typing import Any, Sequence
from re import match, findall
from pickle import load
from networkx import Graph, shortest_path_length
import networkx
from networkx.algorithms.shortest_paths.generic import shortest_path
from itertools import combinations
from bqskit import Circuit
from bqskit.ir.lang.qasm2.qasm2	import OPENQASM2Language


def check_multi(qasm_line) -> tuple[int] | None:
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


def is_same(a : Sequence[int], b : Sequence[int]) -> bool:
	"""True if edges are equivalent."""
	if (a[0], a[1]) == (b[0], b[1]) or (a[1], a[0]) == (b[0], b[1]):
		return True
	else:
		return False


def get_logical_operations(
	circuit: Circuit,
	qudit_group: Sequence[int] | None = None,
	undirected : bool = True
) -> Sequence[Sequence[int]]:
	logical_operations = []
	for op in circuit:
		if len(op.location) > 1:
			for edge in combinations(op.location, 2):
				logical_operations.append(edge)
	if qudit_group is not None:
		logical_operations = [(qudit_group[op[0]], qudit_group[op[1]]) 
			for op in logical_operations]

	if undirected:
		for edge in logical_operations:
			rev_edge = (edge[1], edge[0])
			if rev_edge in logical_operations:
				logical_operations.remove(rev_edge)
				logical_operations.append(edge)

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
		(u,v) for (u,v) in logical_operations if not 
		is_partitionable(physical_topology, qudit_group, (u,v))
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
	graph = hybrid_topology.copy() if qudit_group is None else \
		hybrid_topology.subgraph(qudit_group)
	relabeled_hybrid = hybrid_topology.copy()
	estimate = 0
	for op in operations:
		dist = shortest_path_length(graph, op[0], op[1], weight="weight")
		cost = 3 * (dist - 1) + 1 
		# Do relabeling for unpartitionable gates
		if cost > 1:
			### OPTION A: actually changed physical topology
			## See if logical edge exists
			#if graph.has_edge(op[0], op[1]):
			#	(u,v) = (op[0], op[1])
			#elif graph.has_edge(op[1], op[0]):
			#	(u,v) = (op[1], op[0])
			#else:
			#	estimate += cost
			#	continue
			#best_open = hybrid_topology.number_of_nodes()
			#best_dist = best_open
			#best_inner = qudit_group[0]
			## Find best "open seat"
			#u_open = [x for x in neighbors(graph, u) if x not in qudit_group]
			#if len(u_open) == 0:
			#	u_open = [x for x in qudit_group if x != u and x != v]
			#for x in u_open:
			#	new_dist = shortest_path_length(relabeled_hybrid, v, x, 
			#		weight="weight")
			#	if new_dist < best_dist and new_dist > 0:
			#		best_dist = new_dist
			#		best_open = x
			#		best_inner = v

			#v_open = [x for x in neighbors(graph, v) if x not in qudit_group]
			#if len(v_open) == 0:
			#	v_open = [x for x in qudit_group if x != u and x != v]
			#for x in v_open:
			#	new_dist = shortest_path_length(relabeled_hybrid, u, x, 
			#		weight="weight")
			#	if new_dist < best_dist and new_dist > 0:
			#		best_dist = new_dist
			#		best_open = x
			#		best_inner = u
			#cost = 3 * (best_dist - 1) + 1
			#relabeling = {best_inner: best_open, best_open: best_inner}
			#relabeled_hybrid = relabel_nodes(relabeled_hybrid, relabeling)
			#graph = relabeled_hybrid.subgraph(qudit_group)

			### OPTION B: if logical edges are reused, assume they've been
			### 	changed to physical edges by SWAPs
			###	*May result in underestimates for blocks with many unparti-
			###  tionable gates
			if graph.has_edge(op[0], op[1]):
				graph[op[0]][op[1]]["weight"] = 1
			elif graph.has_edge(op[1], op[0]):
				graph[op[1]][op[0]]["weight"] = 1

		estimate += cost
	return estimate


def collect_stats(
    circuit : Circuit,
    physical_graph : Graph, 
    hybrid_graph : Graph,
    qudit_group : Sequence[int],
    blocksize : int | None = None,
	options : dict[str, Any] | None = None,
) -> str:
    # NOTE: may break if idle qudit are removed
    hybrid_copy = hybrid_graph.copy()
    blocksize = len(qudit_group) if blocksize is None else blocksize
    logical_ops = get_logical_operations(circuit, qudit_group)

    physical = get_physical_edges(logical_ops, physical_graph)
    partitionable = get_partitionable_edges(logical_ops,
        physical_graph, qudit_group)
    unpartitionable = get_unpartitionable_edges(logical_ops,
        physical_graph, qudit_group)

    physical_cost = estimate_cnot_count(physical, hybrid_copy)
    partitionable_cost = estimate_cnot_count(partitionable, hybrid_copy, 
        qudit_group)
    unpartitionable_cost = estimate_cnot_count(unpartitionable, hybrid_copy, 
        qudit_group)
    total_cost = sum([physical_cost, partitionable_cost, unpartitionable_cost])
    stats = (
		f"INFO -\n"
		f"  blocksize: {blocksize}\n"
        f"  block: {qudit_group}\n"
		f"OPERATION COUNTS -\n"
        f"  total operations: {len(logical_ops)}\n"
        f"    physical ops       : {len(physical)}\n"
        f"    partitionable ops  : {len(partitionable)}\n"
        f"    unpartitionable ops: {len(unpartitionable)}\n"
		f"COST ESTIMATES -\n"
        f"  total block CNOTs: {total_cost}\n"
        f"    physical CNOTs       : {physical_cost}\n"
        f"    partitionable CNOTs  : {partitionable_cost}\n"
        f"    unpartitionable CNOTs: {unpartitionable_cost}\n"
    )
    total_ops = sum([len(physical), len(partitionable), len(unpartitionable)])
    if options is not None:
        options["physical_ops"] += len(physical)
        options["physical_cost"] += physical_cost
        options["partitionable_ops"] += len(partitionable)
        options["partitionable_cost"] += partitionable_cost
        options["unpartitionable_ops"] += len(unpartitionable)
        options["unpartitionable_cost"] += unpartitionable_cost
        options["estimated_cnots"] += total_cost
        if total_ops > options["max_block_length"]:
            options["max_block_length"] = total_ops
        if total_ops < options["min_block_length"]:
            options["min_block_length"] = total_ops

    return stats


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
	#return 3 * 2 * (distance)
	# Just the distance
	return distance


def add_logical_edges(
	logical_operations : Sequence[Sequence[int]],
	qudit_group : Sequence[int],
	physical_topology : Graph,
	hybrid_topology : Graph,
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
	unpartitionable_edges = get_unpartitionable_edges(logical_operations, 
		physical_topology, qudit_group)
	
	if options["nearest_physical"]:
		# Shortest path between vertices physically connected to vertex_a and
		# vertices physically connected to vertex_b
		subgraph = physical_topology.subgraph(qudit_group)
		for (vertex_a, vertex_b) in unpartitionable_edges:
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
			for qudit in reachable:
				for other in unreachable:
					dist = shortest_path_length(physical_topology, qudit, other)
					if dist < best_dist and dist > 0:
						best_dist = dist
						best_qudit = qudit
						best_other = other
			hybrid_graph.add_edge(best_qudit, best_other, 
				weight=cost_function(best_dist))
			subgraph = hybrid_graph.subgraph(qudit_group)
			reachable = list(shortest_path(subgraph, qudit_group[0]).keys())

	else: # shortest_direct assumed
		for (vertex_a, vertex_b) in unpartitionable_edges:
			dist = shortest_path_length(physical_topology, vertex_a, vertex_b)
			hybrid_graph.add_edge(vertex_a, vertex_b, 
				weight=cost_function(dist))

	return hybrid_graph


def get_hybrid_topology(
	circuit_file : str, 
	coupling_file : str,
	qudit_group : Sequence[int],
	options : dict[str],
) -> Graph | None:
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
	if options['checkpoint_as_qasm']:
		with open(circuit_file, 'r') as f:
			circuit = OPENQASM2Language().decode(f.read())
	# Pickle format
	else:
		with open(circuit_file, 'rb') as f:
			circuit = pickle.load(f)
	logical_operations = get_logical_operations(circuit, qudit_group)

	# Add edges to graph
	hybrid_graph = add_logical_edges(
		logical_operations,
		qudit_group,
		physical_graph,
		hybrid_graph,
		options
	)
	hybrid_graph.add_weighted_edges_from(physical_edge_set)

	stats_str = collect_stats(circuit, physical_graph, hybrid_graph, 
		qudit_group, options=options)
	print(stats_str)
	return hybrid_graph
