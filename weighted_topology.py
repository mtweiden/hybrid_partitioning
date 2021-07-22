"""
Takes a circuit (qasm file) and a physical topology and produces a hybrid 
logical-physical topology.
"""

from __future__ import annotations
import pickle
import re
from typing import Any, Dict, Sequence, Tuple
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
		u = min(int(q[0]), int(q[1]))
		v = max(int(q[0]), int(q[1]))
		return (u,v)
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
) -> Tuple[Sequence[Sequence[int]], Dict[Tuple[int,int],int]] \
	| Sequence[Sequence[int]]:
	logical_operations = []
	frequencies = {}
	for op in circuit:
		if len(op.location) > 1:
			# TODO: handle multi qubit gates
			#for edge in combinations(op.location, 2):
			#	logical_operations.append(edge)
			if qudit_group is not None:
				a = min([qudit_group[op.location[0]], 
					qudit_group[op.location[1]]])
				b = max([qudit_group[op.location[0]], 
					qudit_group[op.location[1]]])
			else:
				a = min([op.location[0], op.location[1]])
				b = max([op.location[0], op.location[1]])
			logical_operations.append((a,b))
	to_count = set(logical_operations)
	for edge in to_count:
		frequencies[edge] = logical_operations.count(edge)
	return (logical_operations, frequencies)


def is_internal(
	physical_topology: Graph,
	qudit_group: Sequence[int],
	edge: tuple[int]
) -> bool:
	subgraph = physical_topology.subgraph(qudit_group)
	try:
		return shortest_path_length(subgraph,edge[0],edge[1]) < len(qudit_group)
	except networkx.exception.NetworkXNoPath:
		return False


def get_external_edges(
	logical_operations : Sequence[Sequence[int]],
	physical_topology : Graph,
	qudit_group : Sequence[int],
) -> Sequence[Sequence[int]]:
	"""
	Gates that require a logical edge to be inserted into the hybrid topology.
	"""
	return [
		(u,v) for (u,v) in logical_operations if not 
		is_internal(physical_topology, qudit_group, (u,v))
	]


def get_indirect_edges(
	logical_operations : Sequence[Sequence[int]],
	physical_topology : Graph,
	qudit_group : Sequence[int],
) -> Sequence[Sequence[int]]:
	"""
	Gates that can be implemented on physical edges but non adjacent vertices.
	"""
	physical = get_direct_edges(logical_operations, physical_topology)
	internal = [
		edge for edge in logical_operations if 
		is_internal(physical_topology, qudit_group, edge)
	]
	non_physical = [
		(u,v) for (u,v) in internal if 
		(u,v) not in physical and (v,u) not in physical
	]
	return non_physical


def get_direct_edges(
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


def apply_frequencies(
	logical_operations : Sequence[Sequence[int]],
	hybrid_topology : Graph,
) -> Graph:
	hybrid_graph = hybrid_topology.copy()
	for (u,v) in hybrid_graph.edges:
		hybrid_graph[u][v]["frequency"] = 0
	# Increment the frequency for each edge involved in some operation
	for (u,v) in logical_operations:
		path = shortest_path(hybrid_graph, u, v)
		for i in range(len(path) - 1):
			if hybrid_graph.has_edge(path[i], path[i+1]):
				hybrid_graph[path[i]][path[i+1]]["frequency"] += 1
	return hybrid_graph


def get_volume(
	operations : Sequence[Sequence[int]],
	hybrid_topology : Graph,
) -> int:
	"""
	Make sure that apply_freqencies has already been called!!
	"""
	#ops = set(operations)
	ops = operations
	volume = 0
	for (u,v) in ops:
		path = shortest_path(hybrid_topology, u, v)
		for i in range(len(path) - 1):
			#freq = hybrid_topology[path[i]][path[i+1]]["frequency"]
			dist = hybrid_topology[path[i]][path[i+1]]["weight"]
			#volume += freq / dist
			volume += dist

	return volume


def estimate_cnot_count(
	operations : Sequence[Sequence[int]],
	hybrid_topology : Graph,
	qudit_group : Sequence[int] | None = None,
) -> int:
	graph = hybrid_topology.copy() if qudit_group is None else \
		hybrid_topology.subgraph(qudit_group)
	estimate = 0
	for op in operations:
		dist = shortest_path_length(graph, op[0], op[1], weight="weight")
		cost = 3 * (dist - 1) + 1 
		# Do relabeling for external gates
		if cost > 1:
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
    logical_ops, freqs = get_logical_operations(circuit, qudit_group)
    hybrid_copy = apply_frequencies(logical_ops, hybrid_copy)

    direct = get_direct_edges(logical_ops, physical_graph)
    indirect = get_indirect_edges(logical_ops,
        physical_graph, qudit_group)
    external = get_external_edges(logical_ops,
        physical_graph, qudit_group)

    direct_volume = get_volume(direct, hybrid_copy)
    indirect_volume = get_volume(indirect, hybrid_copy) 
    external_volume = get_volume(external, hybrid_copy) 
    #direct_cost = estimate_cnot_count(direct, hybrid_copy)
    #indirect_cost = estimate_cnot_count(indirect, hybrid_copy, qudit_group)
    #external_cost = estimate_cnot_count(external, hybrid_copy, qudit_group)
    total_volume = sum([direct_volume, indirect_volume, external_volume])
    #total_cost = sum([direct_cost, indirect_cost, external_cost])

    logical_edges = [(u,v) for (u,v) in hybrid_graph.edges if (u,v) 
        not in physical_graph.edges and (v,u) not in physical_graph.edges]

    stats = (
		f"INFO -\n"
		f"  blocksize: {blocksize}\n"
        f"  block: {qudit_group}\n"
		f"OPERATION COUNTS & VOLUME-\n"
        f"  total distinct operations : {len(logical_ops)}\n"
        f"  total block volume : {total_volume}\n"
        f"    direct ops      : {len(direct)}\n"
        f"    direct volume   : {direct_volume}\n"
        f"    indirect ops    : {len(indirect)}\n"
        f"    indirect volume : {indirect_volume}\n"
        f"    external ops    : {len(external)}\n"
        f"    external volume : {external_volume}\n"
		#f"ESTIMATED COST -\n  cnots : {total_cost}\n"
		f"SUBTOPOLOGY -\n"
		f"  number of edges : {len(list(hybrid_copy.edges))}\n"
		f"  number of logical : {len(logical_edges)}\n"
    )
	# TODO: get freqency from indirect and external operations, not just
	# direct edges
	# TODO: how to get distance when logical edges sometimes use density?
    #for edge in hybrid_copy.edges:
    #    estr = f"({edge[0]}, {edge[1]}) - distance: {} - frequency: {}\n"

    total_ops = sum([len(direct), len(indirect), len(external)])

    if options is not None:
        options["direct_ops"] += len(direct)
        options["direct_volume"] += direct_volume
        options["indirect_ops"] += len(indirect)
        options["indirect_volume"] += indirect_volume
        options["external_ops"] += len(external)
        options["external_volume"] += external_volume
        options["total_volume"] += total_volume
        #options["estimated_cnots"] += total_cost
        if total_ops > options["max_block_length"]:
            options["max_block_length"] = total_ops
        if total_ops < options["min_block_length"] or \
			options["min_block_length"] == 0:
            options["min_block_length"] = total_ops

    return stats


def cost_function(distance: int, frequency: int) -> float:
	"""
	Give the density (path distance / frequency) of the edge.

	Args:
		distance (int): Shortest path distance in the physical topology.

		frequency (int): Number of occurences of an edge in the circuit.

	Returns:
		cost (int): The result of the cost function. 
	"""
	# Number of CNOTs needed to SWAP
	#return 3 * 2 * (distance)
	# Density
	return distance / frequency


def add_logical_edges(
	logical_operations : Sequence[Sequence[int]],
	frequencies : Dict[Tuple[int,int], int],
	qudit_group : Sequence[int],
	physical_topology : Graph,
	hybrid_topology : Graph,
	options : dict[str],
) -> Graph:
	"""
	Add a logical edge to either hybrid graph based off the options passed.

	Args:
		logical_operations (list[tuple[int]]): The logical operations that may
		    require the addition of logical edges.

		frequencies (Dict[Tuple[int,int], int]): The number of times each edge
			appears in the circuit.

		qudit_group (Sequence[int]): The qudits in the current block.

		physical_topology (Graph): Graph of the physical topology.

		hybrid_topology (Graph): Graph of the hybrid topology.

		options (dict[str, Any]): 
			shortest_path (bool): Connect vertices as end points using the
				shortest direct path in the physical topology. Weights 
				represent the shortest path distance in the physical topology.
				(default)

			nearest_physical (bool): Add logical edges between members of the
				qudit_group. Considers the two separate possibly disjoint 
				connected components containing vertex_a and vertex_b, and 
				finds the shortest path between these two sets. Here, logical
				edges do not directly correspond with edges in the circuit.
				Weights represent the shortest path distance in the physical
				topology.

			mst_path (bool): Construct an Minimum Spanning Tree for the
				subgraph containing members of the qudit group. Weights 
				represent the shortest path distance in the physical topology.
				This means edges are added in order of least to greatest path
				length.

			mst_density (bool): Construct an Minimum Spanning Tree for the
				subgraph containing members of the qudit group. Weights 
				represent the edge's density, or the shortest path distance in 
				the physical topology / the edge's frequency. This means edges
				are added in order of least to greatest density.
			
			TODO: Handle case where MST isn't enough, when do we need to add
				more logical edges?
		
	Returns:
		updated_graph (Graph): Return the new hybird_graph.
	"""
	hybrid_graph = hybrid_topology.copy()
	external_edges = get_external_edges(logical_operations, 
		physical_topology, qudit_group)
	
	if options["nearest_physical"]:
		# Shortest path between vertices physically connected to vertex_a and
		# vertices physically connected to vertex_b
		subgraph = physical_topology.subgraph(qudit_group)

		for (vertex_a, vertex_b) in external_edges:
			candidates_a = list(shortest_path(subgraph, vertex_a).keys())
			candidates_b = list(shortest_path(subgraph, vertex_b).keys())
			best_dist = physical_topology.number_of_nodes()
			best_a = vertex_a
			best_b = vertex_b
			for a in candidates_a:
				for b in candidates_b:
					dist = shortest_path_length(physical_topology, a, b)
					if dist < best_dist and dist > 0:
						best_dist = dist
						best_a = a
						best_b = b
				hybrid_graph.add_edge(
					best_a, best_b, weight=best_dist,
				)
	
	elif options["mst_path"] or options["mst_density"]:
		# Build a MST in the subgraph by adding the lowest density edges first
		subgraph = physical_topology.subgraph(qudit_group)
		# Find all disconected subgroups, add the closest
		search_qubit = 0
		reachable = list(shortest_path(subgraph, qudit_group[0]).keys())
		op_set = set(logical_operations)
		# While there are still disconnected subgroups
		while len(reachable) < len(qudit_group):
			# Find logical operations that corresponds to edges on vertices
			# that are disconnected. Add then based on least to greatest
			# density
			unreachable = list(set(qudit_group) - set(reachable))
			candidates = []
			for (u,v) in op_set:
				if (
					u in reachable and v in unreachable or
					v in reachable and u in unreachable
				):
					distance = shortest_path_length(physical_topology, u, v)
					frequency = frequencies[(u,v)]
					candidates.append((u, v, distance, frequency))
			# If candidates is empty, that means we have two disjoint sets of
			# qudits that never interact, so we're done
			if len(candidates) == 0:
				if search_qubit >= len(qudit_group) - 1:
					break
				else:
					search_qubit += 1
					subgraph = hybrid_graph.subgraph(qudit_group)
					reachable = list(shortest_path(subgraph, 
						qudit_group[search_qubit]).keys())
					continue
			if options["mst_density"]:
				candidates = sorted(candidates, key=lambda x: x[2]/x[3])
			else:
				candidates = sorted(candidates, key=lambda x: x[2])
			# Frequencies will be added afte all logical edges have been added
			(u, v, weight, _) = candidates[0]
			hybrid_graph.add_edge(u, v, weight=weight)
			subgraph = hybrid_graph.subgraph(qudit_group)
			reachable = list(shortest_path(subgraph, 
				qudit_group[search_qubit]).keys())


	else: # shortest_path or shortest_density assumed
		subgraph = physical_topology.subgraph(qudit_group)
		for op in logical_operations:
			if not is_internal(physical_topology, qudit_group, op):
				dist = shortest_path_length(
					physical_topology,
					op[0],
					op[1],
				)
				hybrid_graph.add_edge(
					op[0],
					op[1],
					weight=dist
				)

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
			blocksize (int): Defines the size of qudit groups
			is_qasm (bool): Whether the circuit_file is qasm or pickle.

	Returns:
		hybrid_edge_set (set[tuple[int]]): The physical topology with logical
			edges added for unpartitionable gates.
	
	Raises:
		ValueError: If `blocksize` key is not in `options`.
	"""
	if "blocksize" not in options:
		raise ValueError("The `blocksize` entry in	`options` is required.")

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

	# QASM format
	if options['checkpoint_as_qasm']:
		with open(circuit_file, 'r') as f:
			circuit = OPENQASM2Language().decode(f.read())
	# Pickle format
	else:
		with open(circuit_file, 'rb') as f:
			circuit = pickle.load(f)
	logical_ops, freqs = get_logical_operations(circuit, qudit_group)

	# Add edges to graph
	hybrid_graph = add_logical_edges(
		logical_ops,
		freqs,
		qudit_group,
		physical_graph,
		hybrid_graph,
		options
	)
	hybrid_graph.add_weighted_edges_from(physical_edge_set)

	stats_str = collect_stats(circuit, physical_graph, hybrid_graph, 
		qudit_group, options=options)
	print(stats_str)
	with open(f"{options['subtopology_dir']}/summary.txt", "a") as f:
		f.write(f"\n{circuit_file.split('/')[-1]}\n")
		f.write(stats_str)
	return hybrid_graph
