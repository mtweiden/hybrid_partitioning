"""
Takes a circuit (qasm file) and a physical topology and produces a hybrid 
logical-physical topology.
"""

from __future__ import annotations
import itertools
from logging import log
import pickle
from posix import listdir
import re
from sys import intern
from typing import Any, Dict, Sequence, Tuple
from re import match, findall
from pickle import load

from networkx.classes.function import degree

from util import get_mapping_results, get_original_count, get_remapping_results, load_block_circuit, load_block_topology
from networkx import Graph, shortest_path_length
import networkx
from networkx.algorithms.shortest_paths.generic import shortest_path
from itertools import combinations
from bqskit import Circuit
from bqskit.ir.lang.qasm2.qasm2	import OPENQASM2Language
from networkx.generators.ego import ego_graph


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
) -> Sequence[Sequence[int]]:
	logical_operations = []
	for op in circuit:
		if len(op.location) > 1:
			# TODO: handle multi qubit gates
			if qudit_group is not None:
				a = min([qudit_group[op.location[0]], 
					qudit_group[op.location[1]]])
				b = max([qudit_group[op.location[0]], 
					qudit_group[op.location[1]]])
			else:
				a = min([op.location[0], op.location[1]])
				b = max([op.location[0], op.location[1]])
			logical_operations.append((a,b))
	return logical_operations


def get_frequencies(
	circuit: Circuit,
	qudit_group: Sequence[int] | None = None,
) -> Dict[Tuple, int]:
	frequencies = {}
	logical_operations = []
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
	return frequencies


def is_internal(
	physical_topology: Graph,
	qudit_group: Sequence[int],
	edge: tuple[int],
) -> bool:
	# Check for a path in the subgraph if no blocksize is provided
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
	direct = get_direct_edges(logical_operations, physical_topology)
	internal = [
		edge for edge in logical_operations if 
		is_internal(physical_topology, qudit_group, edge)
	]
	indirect = [
		(u,v) for (u,v) in internal if 
		(u,v) not in direct and (v,u) not in direct
	]
	return indirect 


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


def collect_stats_tuples(
	circuit : Circuit,
	physical_graph : Graph, 
	kernel : Graph | Sequence[tuple[int]],
	qudit_group : Sequence[int],
	blocksize : int | None = None,
	options : dict[str, Any] | None = None,
) -> Sequence:
	# NOTE: may break if idle qudit are removed
	blocksize = len(qudit_group) if blocksize is None else blocksize
	logical_ops = get_logical_operations(circuit, qudit_group)

	direct = get_direct_edges(logical_ops, physical_graph)
	indirect = get_indirect_edges(logical_ops, physical_graph, qudit_group)
	external = get_external_edges(logical_ops, physical_graph, qudit_group)

	active_qudits = circuit.get_active_qudits()

	total_ops = sum([len(direct), len(indirect), len(external)])

	pre_stats = (
		# active qudits
		len(active_qudits),
		# direct ops
		len(direct),
		# indirect ops
		len(indirect),
		# external ops
		len(external),
		# cnot count
		total_ops,
	)

	subtopology_stats = (
		# number of edges
		len(kernel),
		# Kernel name
		kernel_name(kernel, blocksize)
	)

	return (pre_stats, subtopology_stats)


def kernel_name(kernel, blocksize) -> str:
	if len(kernel) == 4:
		kernel_type = "ring"
	elif len(kernel) < 3:
		kernel_type = "linear"
	else:
		# kernel is a star if there is a degree 3 vertex
		degrees = {x:0 for x in range(blocksize)}
		for edge in kernel:
			degrees[edge[0]] += 1
			degrees[edge[1]] += 1
		if max(degrees.values()) == 3:
			kernel_type = "star"
		elif max(degrees.values()) == 2:
			kernel_type = "linear"
		else:
			kernel_type = "unknown"
	return kernel_type


def collect_stats(
	circuit : Circuit,
	physical_graph : Graph, 
	kernel: Sequence[tuple[int]],
	qudit_group : Sequence[int],
	blocksize : int | None = None,
	options : dict[str, Any] | None = None,
) -> str:
	# NOTE: may break if idle qudit are removed
	blocksize = len(qudit_group) if blocksize is None else blocksize
	logical_ops = get_logical_operations(circuit, qudit_group)

	direct = get_direct_edges(logical_ops, physical_graph)
	indirect = get_indirect_edges(logical_ops, physical_graph, qudit_group)
	external = get_external_edges(logical_ops, physical_graph, qudit_group)
	
	active_qudits = circuit.get_active_qudits()

	kernel_type = kernel_name(kernel, blocksize)

	stats = (
		f"INFO -\n"
		f"  blocksize: {blocksize}\n"
		f"  block: {qudit_group}\n"
		f"  active: {len(active_qudits)}\n"
		f"  cnot count: {len(logical_ops)}\n"
		f"OPERATION COUNTS & VOLUME-\n"
		f"	direct ops	  : {len(direct)}\n"
		f"	indirect ops	: {len(indirect)}\n"
		f"	external ops	: {len(external)}\n"
		f"SUBTOPOLOGY -\n"
		f"  kernel : {kernel_type}"
		f"  {kernel}"
		f"  number of edges : {len(list(kernel))}\n"
	)

	total_ops = sum([len(direct), len(indirect), len(external)])

	if options is not None:
		options["direct_ops"] += len(direct)
		options["indirect_ops"] += len(indirect)
		options["external_ops"] += len(external)
		if total_ops > options["max_block_length"]:
			options["max_block_length"] = total_ops
		if total_ops < options["min_block_length"] or \
			options["min_block_length"] == 0:
			options["min_block_length"] = total_ops

	return stats


def get_num_vertex_uses(logical_operations, num_qudits) -> dict[int,int]:
	degrees = {x:0 for x in range(num_qudits)}
	for a,b in logical_operations:
		degrees[a] += 1
		degrees[b] += 1
	return degrees

# NOTE: only to be used for 4 qudits
def best_line_kernel(op_set, freqs) -> Sequence[tuple[int]]:
	edges = sorted(list(op_set), key=lambda x: freqs[x], reverse=True)
	kernel_edges = []
	if len(edges) < 3:
		return edges
	else:
		used_qudits = set([])
		for i in range(2):
			kernel_edges.append(edges[i])
			used_qudits.add(edges[i][0])
			used_qudits.add(edges[i][1])
		for i in range(2,len(edges)):
			if edges[i][0] in used_qudits and edges[i][1] in used_qudits:
				if len(kernel_edges) == 2 and len(used_qudits) == 4:
					kernel_edges.append(edges[i])
					break
			else:
				kernel_edges.append(edges[i])
				break

		return kernel_edges

# NOTE: only to be used for 4 qudits
def best_ring_kernel(op_set, freqs) -> Sequence[tuple[int]]:
	# Keep the first 3 edges. If there's a star, remove the third edge
	# and form a ring. If there's a line, add the last edge to make it
	# a ring.
	edges = sorted(list(op_set), key=lambda x: freqs[x], reverse=True)

	kernel_edges = [edges[x] for x in range(3)]
	degrees = get_num_vertex_uses(kernel_edges, 4)
	v = sorted(degrees.keys(), key=lambda x: degrees[x], reverse=True)
	# Handling star
	if degrees[v[0]] == 3:
		removed_edge = kernel_edges.pop(-1)
		corner_vertex = removed_edge[0] if removed_edge[0] != v[0] \
			else removed_edge[1]
		# Add other 2 edges to make a  ring
		for i in range(1,4):
			if corner_vertex != v[i]:
				kernel_edges.append((corner_vertex, v[i]))
	# Handling line
	else:
		# add edge between the two vertices with degree 1
		kernel_edges.append((v[-1], v[-2]))
	return kernel_edges


def best_star_kernel(vertex_uses) -> Sequence[tuple[int]]:
	# Return the star graph with the most used vertex in the center.
	q = sorted(vertex_uses.keys(), key=lambda x: vertex_uses[x],
		reverse=True)
	return [(q[1],q[0]), (q[2],q[0]), (q[3],q[0])]


def select_linear_kernel(
	circuit_file : str, 
	qudit_group : Sequence[int],
	options : dict[str],
) -> Sequence[tuple[int]]:
	if "blocksize" not in options:
		raise ValueError("The `blocksize` entry in	`options` is required.")
	elif options["blocksize"] > 5:
		raise RuntimeError(
			"Only blocksizes up to 5 are currently supported."
		)

	# Convert the physical topology to a networkx graph
	circuit = load_block_circuit(circuit_file, options)
	logical_ops = get_logical_operations(circuit)
	op_set = set(logical_ops)
	freqs = get_frequencies(circuit)

	ranked_ops = sorted(list(op_set), key=lambda x: freqs[x], reverse=True)

	vertex_degrees = get_num_vertex_uses(op_set, len(qudit_group))

	edges = []
	# TODO: Generalize kernel selection for blocksizes > 4
	# Handle the case where there are no multi-qubit gates
	while len(ranked_ops) > 0:
		edges.append(ranked_ops.pop(0))	
		# 1 edge cases:
		#	K_2
		# 2 edges cases:
		#	2 disconnected K_2 graphs
		#	3-line
		if len(edges) <= 2:
			continue
		# 3 edges cases:
		#	K_3 (revert)
		#		degrees - 2, 2, 2, 0, 0
		#	4-star (pick new edge)
		#		degrees - 3, 1, 1, 1, 0
		#	4-line
		#		degrees - 2, 2, 1, 1, 0
		#	Disconnected K_2 and 3-line
		#		degrees - 2, 1, 1, 1, 1
		elif len(edges) == 3:
			vertex_degrees = get_num_vertex_uses(edges, options["blocksize"])
			d = sorted(list(vertex_degrees.values()), reverse=True)
			if (
				d[0] == 2 and d[1] == 2 and d[2] == 2
			) or options["blocksize"] > 3 and (
				d[0] == 3 and d[1] == 1 and d[2] == 1 and d[3] == 1
			):
				removed_edge = edges.pop(-1)
				# If no more edges to choose from, connect the node to one of
				# the end nodes
				center = removed_edge[0] if vertex_degrees[removed_edge[0]] == 3 \
					else removed_edge[1]
				new_node = removed_edge[0] if center != removed_edge[0] \
					else removed_edge[1]
				for i in vertex_degrees.keys():
					if vertex_degrees[i] == 1 and i != new_node:
						break
				new_edge = (min(new_node, i), max(new_node, i))
				edges.append(new_edge)
			continue
		# 4 edges cases:
		#	4-dipper (revert)
		#		degrees - 3, 2, 2, 1, 0
		#	4-ring (revert)
		#		degrees - 2, 2, 2, 2, 0
		#	disconnected K_2 and K_3 (revert)
		#		degrees - 2, 2, 2, 1, 1
		#	5-tee (pick new edge)
		#		degrees - 3, 2, 1, 1, 1
		#	5-line
		#		degrees - 2, 2, 2, 1, 1
		elif len(edges) == 4:
			vertex_degrees = get_num_vertex_uses(edges, options["blocksize"])
			d = sorted(list(vertex_degrees.values()), reverse=True)
			if options["blocksize"] < 5 and (
				d[0] == 3 and d[1] == 2 and d[2] == 2 and d[3] == 1
			) or (
				d[0] == 2 and d[1] == 2 and d[2] == 2 and d[3] == 2
			):
				edges.pop(-1)
			elif options["blocksize"] > 4 and (
				d[0] == 3 and d[1] == 2 and d[2] == 1 and d[3] == 1 and d[4] == 1
			):
				removed_edge = edges.pop(-1)
				# If no more edges to choose from, connect the node to an end node
				# preferably the one closest to the center node
				center = removed_edge[0] if vertex_degrees[removed_edge[0]] == 3 \
					else removed_edge[1]
				new_node = removed_edge[0] if center != removed_edge[0] \
					else removed_edge[1]
				for i in vertex_degrees.keys():
					if vertex_degrees[i] == 1 and i != new_node:
						break
				for j in vertex_degrees.keys():
					if vertex_degrees[j] == 1 and j != new_node and j != i:
						break
				# Find the end node closest to the center node
				if (i, center) or (center, i) in edges:
					new_edge = (min(new_node, i), max(new_node, i))
				else:
					new_edge = (min(new_node, j), max(new_node, j))
				edges.append(new_edge)

			elif options["blocksize"] > 4 and (
				d[0] == 2 and d[1] == 2 and d[2] == 2 and d[3] == 1 and d[4] == 1
			):
				# If the degree 1 nodes are adjacent, revert
				for i in vertex_degrees.keys():
					if vertex_degrees[i] == 1:
						break
				for j in vertex_degrees.keys():
					if vertex_degrees[j] == 1 and i != j:
						break
				if (i,j) in edges or (j,i) in edges:
					edges.pop(-1)
			continue
		# 5 edges cases:
		# Only blocksize 5 is supported
		elif len(edges) > 4:
			edges.pop(-1)

	return edges


def select_falcon_kernel(
	circuit_file : str, 
	qudit_group : Sequence[int],
	options : dict[str],
) -> Sequence[tuple[int]]:
	"""
	Given a qasm file and a physical topology, produce a hybrid topology where
	logical edges are added for unperformable gates.

	Args:
		circuit_file (str): Path to the file specifying the circuit block.

		qudit_group (Sequence[int]): Only qudit_group members will be used as
			end points of logical edges.

		options (dict[str]): 
			blocksize (int): Defines the size of qudit groups
			is_qasm (bool): Whether the circuit_file is qasm or pickle.
			kernel_dir (str): Directory in which the kernel files are stored.

	Returns:
		kernel_edge_set (set[tuple[int]]): Edges to be used for synthesis.
	
	Raises:
		ValueError: If `blocksize` key is not in `options`.
	"""
	if "blocksize" not in options:
		raise ValueError("The `blocksize` entry in	`options` is required.")
	elif options["blocksize"] > 5:
		raise RuntimeError(
			"Only blocksizes up to 5 are currently supported."
		)

	# Convert the physical topology to a networkx graph
	circuit = load_block_circuit(circuit_file, options)
	logical_ops = get_logical_operations(circuit)
	op_set = set(logical_ops)
	freqs = get_frequencies(circuit)

	ranked_ops = sorted(list(op_set), key=lambda x: freqs[x], reverse=True)

	vertex_degrees = get_num_vertex_uses(op_set, len(qudit_group))

	edges = []
	# TODO: Generalize kernel selection for blocksizes > 4
	# Handle the case where there are no multi-qubit gates
	while len(ranked_ops) > 0:
		edges.append(ranked_ops.pop(0))	
		# 1 edge cases:
		#	K_2
		# 2 edges cases:
		#	2 disconnected K_2 graphs
		#	3-line
		if len(edges) <= 2:
			continue
		# 3 edges cases:
		#	K_3 (revert)
		#		degrees - 2, 2, 2, 0, 0
		#	4-star
		#		degrees - 3, 1, 1, 1, 0
		#	4-line
		#		degrees - 2, 2, 1, 1, 0
		#	Disconnected K_2 and 3-line
		#		degrees - 2, 1, 1, 1, 1
		elif len(edges) == 3:
			vertex_degrees = get_num_vertex_uses(edges, options["blocksize"])
			d = sorted(list(vertex_degrees.values()), reverse=True)
			if (
				d[0] == 2 and d[1] == 2 and d[2] == 2
			):
				edges.pop(-1)
			continue
		# 4 edges cases:
		#	4-dipper (revert)
		#		degrees - 3, 2, 2, 1, 0
		#	4-ring (revert)
		#		degrees - 2, 2, 2, 2, 0
		#	disconnected K_2 and K_3 (revert)
		#		degrees - 2, 2, 2, 1, 1
		#	5-star (pick new edge)
		#		degrees - 4, 1, 1, 1, 1
		#	5-tee
		#		degrees - 3, 2, 1, 1, 1
		#	5-line
		#		degrees - 2, 2, 2, 1, 1
		elif len(edges) == 4:
			vertex_degrees = get_num_vertex_uses(edges, options["blocksize"])
			d = sorted(list(vertex_degrees.values()), reverse=True)
			if (
				d[0] == 3 and d[1] == 2 and d[2] == 2 and d[3] == 1
			):
				edges.pop(-1)
			elif options["blocksize"] > 4 and(
				d[0] == 4 and d[1] == 1 and d[2] == 1 and d[3] == 1 and d[4] == 1
			):
				removed_edge = edges.pop(-1)
				# If no more edges to choose from, connect the node to an end node
				# preferably the one closest to the center node
				center = removed_edge[0] if vertex_degrees[removed_edge[0]] == 4 \
					else removed_edge[1]
				new_node = removed_edge[0] if center != removed_edge[0] \
					else removed_edge[1]
				for i in vertex_degrees.keys():
					if vertex_degrees[i] == 1 and i != new_node:
						break
				for j in vertex_degrees.keys():
					if vertex_degrees[j] == 1 and j != new_node and j != i:
						break
				for k in vertex_degrees.keys():
					if vertex_degrees[k] == 1 and k != new_node and k != i and k!= j:
						break
				new_edge_i = (min(i, new_node), max(i, new_node))
				new_edge_j = (min(j, new_node), max(j, new_node))
				new_edge_k = (min(k, new_node), max(k, new_node))
				if new_edge_i in ranked_ops:
					edges.append(new_edge_i)
				elif new_edge_j in ranked_ops:
					edges.append(new_edge_j)
				elif new_edge_k in ranked_ops:
					edges.append(new_edge_k)
				else:
					edges.append(new_edge_i)
				
				# Find the end node closest to the center node
				if (i, center) or (center, i) in edges:
					new_edge = (min(new_node, i), max(new_node, i))
				else:
					new_edge = (min(new_node, j), max(new_node, j))
				edges.append(new_edge)
			elif options["blocksize"] > 4 and (
				d[0] == 2 and d[1] == 2 and d[2] == 2 and d[3] == 1 and d[4] == 1
			):
				# If the degree 1 nodes are adjacent, revert
				for i in vertex_degrees.keys():
					if vertex_degrees[i] == 1:
						break
				for j in vertex_degrees.keys():
					if vertex_degrees[j] == 1 and i != j:
						break
				if (i,j) in edges or (j,i) in edges:
					edges.pop(-1)
			continue
		# 5 edges cases:
		# Only blocksize 5 is supported
		elif len(edges) > 4:
			edges.pop(-1)

	return edges


def select_mesh_kernel(
	circuit_file : str, 
	qudit_group : Sequence[int],
	options : dict[str],
) -> Sequence[tuple[int]]:
	"""
	Given a qasm file and a physical topology, produce a hybrid topology where
	logical edges are added for unperformable gates.

	Args:
		circuit_file (str): Path to the file specifying the circuit block.

		qudit_group (Sequence[int]): Only qudit_group members will be used as
			end points of logical edges.

		options (dict[str]): 
			blocksize (int): Defines the size of qudit groups
			is_qasm (bool): Whether the circuit_file is qasm or pickle.
			kernel_dir (str): Directory in which the kernel files are stored.

	Returns:
		kernel_edge_set (set[tuple[int]]): Edges to be used for synthesis.
	
	Raises:
		ValueError: If `blocksize` key is not in `options`.
	"""
	if "blocksize" not in options:
		raise ValueError("The `blocksize` entry in	`options` is required.")
	elif options["blocksize"] > 5:
		raise RuntimeError(
			"Only blocksizes up to 5 are currently supported."
		)

	# Convert the physical topology to a networkx graph
	circuit = load_block_circuit(circuit_file, options)
	logical_ops = get_logical_operations(circuit)
	op_set = set(logical_ops)
	freqs = get_frequencies(circuit)

	ranked_ops = sorted(list(op_set), key=lambda x: freqs[x], reverse=True)

	vertex_degrees = get_num_vertex_uses(op_set, len(qudit_group))

	edges = []
	# TODO: Generalize kernel selection for blocksizes > 4
	# Handle the case where there are no multi-qubit gates
	while len(ranked_ops) > 0:
		edges.append(ranked_ops.pop(0))	
		# 1 edge cases:
		#	K_2
		# 2 edges cases:
		#	2 disconnected K_2 graphs
		#	3-line
		if len(edges) <= 2:
			continue
		# 3 edges cases:
		#	K_3 (revert)
		#		degrees - 2, 2, 2, 0, 0
		#	4-star
		#		degrees - 3, 1, 1, 1, 0
		#	4-line
		#		degrees - 2, 2, 1, 1, 0
		#	Disconnected K_2 and 3-line
		#		degrees - 2, 1, 1, 1, 1
		elif len(edges) == 3:
			vertex_degrees = get_num_vertex_uses(edges, options["blocksize"])
			d = sorted(list(vertex_degrees.values()), reverse=True)
			if (
				d[0] == 2 and d[1] == 2 and d[2] == 2
			):
				edges.pop(-1)
			continue
		# 4 edges cases:
		#	4-dipper (revert)
		#		degrees - 3, 2, 2, 1, 0
		#	4-ring
		#		degrees - 2, 2, 2, 2, 0
		#	disconnected K_2 and K_3 (revert)
		#		degrees - 2, 2, 2, 1, 1
		#	5-star
		#		degrees - 4, 1, 1, 1, 1
		#	5-tee
		#		degrees - 3, 2, 1, 1, 1
		#	5-line
		#		degrees - 2, 2, 2, 1, 1
		elif len(edges) == 4:
			vertex_degrees = get_num_vertex_uses(edges, options["blocksize"])
			d = sorted(list(vertex_degrees.values()), reverse=True)
			if (
				d[0] == 3 and d[1] == 2 and d[2] == 2 and d[3] == 1
			):
				edges.pop(-1)
			elif options["blocksize"] > 4 and (
				d[0] == 2 and d[1] == 2 and d[2] == 2 and d[3] == 1 and d[4] == 1
			):
				# If the degree 1 nodes are adjacent, revert
				for i in vertex_degrees.keys():
					if vertex_degrees[i] == 1:
						break
				for j in vertex_degrees.keys():
					if vertex_degrees[j] == 1 and i != j:
						break
				if (i,j) in edges or (j,i) in edges:
					edges.pop(-1)
			continue
		# 5 edges cases:
		#	4-ring with bridge (revert)
		#		degrees - 3, 3, 2, 2, 0
		#	5-star plus extra edge (revert)
		#		degrees - 4, 2, 2, 1, 1
		#	K_3 with 2 branches (revert)
		#		degrees - 3, 3, 2, 1, 1
		#	5-ring (revert)
		#		degrees - 2, 2, 2, 2, 2
		#	4-dipper with long handle (revert)
		#		degrees - 3, 2, 2, 2, 1
		#		Check for embedded K_3 to distinguish from 5 dipper
		#	5-dipper
		#		degrees - 3, 2, 2, 2, 1
		elif len(edges) == 5:
			vertex_degrees = get_num_vertex_uses(edges, options["blocksize"])
			d = sorted(list(vertex_degrees.values()), reverse=True)
			if options["blocksize"] <= 4 and (
				d[0] == 3 and d[1] == 3 and d[2] == 2 and d[3] == 2
			):
				edges.pop(-1)
			elif options["blocksize"] > 4 and ((
				d[0] == 4 and d[1] == 2 and d[2] == 2 and d[3] == 1 and d[4] == 1
			) or (
				d[0] == 3 and d[1] == 3 and d[2] == 2 and d[3] == 1 and d[4] == 1
			) or (
				d[0] == 2 and d[1] == 2 and d[2] == 2 and d[3] == 2 and d[4] == 2
			) or (
				d[0] == 3 and d[1] == 3 and d[2] == 2 and d[3] == 2 and d[4] == 0
			)):
				edges.pop(-1)
			elif (
				d[0] == 3 and d[1] == 3 and d[2] == 2 and d[3] == 1 and d[4] == 1
			):
				# Check to see if the degree 1 vertex is adjacent to the degree 3
				# vertex. If not, pop edge, K_3 embedded
				for i in vertex_degrees.keys():
					if vertex_degrees[i] == 1:
						break
				for j in vertex_degrees.keys():
					if vertex_degrees[3] == 3:
						break
				if (i,j) in edges or (j,i) in edges:
					edges.pop(-1)
			continue
		# Only blocksize 5 is supported
		elif len(edges) > 5:
			edges.pop(-1)

	return edges


def run_stats(
	options : dict[str, Any],
	post_stats : bool = False,
	resynthesized : bool = False,
	remapped : bool = False,
) -> str:
	# Get the subtopology files
	sub_files = listdir(options["subtopology_dir"])
	sub_files.remove(f"summary.txt")
	sub_files = sorted(sub_files)

	# Get the block files
	if not post_stats:
		block_files = listdir(options["partition_dir"])
		block_files.remove(f"structure.pickle")
	else:
		if not resynthesized:
			blocks = listdir(options["synthesis_dir"])
		else:
			blocks = listdir(options["resynthesis_dir"])
		block_files = []
		for bf in blocks:
			if bf.endswith(".qasm"):
				block_files.append(bf)
	block_files = sorted(block_files)

	# Init all the needed variables
	options["direct_ops"]      = 0 
	options["indirect_ops"]    = 0 
	options["external_ops"]    = 0 

	# Get the qudit group
	with open(f"{options['partition_dir']}/structure.pickle", "rb") as f:
		structure = pickle.load(f)

	# Run collect_stats on each block
	for block_num in range(len(block_files)):
		# Get BQSKIT circuit
		if not post_stats:
			with open(f"{options['partition_dir']}/{block_files[block_num]}", 
				"r") as qasm:
				circ = OPENQASM2Language().decode(qasm.read())
		elif not resynthesized:
			with open(f"{options['synthesis_dir']}/{block_files[block_num]}", 
				"r") as qasm:
				circ = OPENQASM2Language().decode(qasm.read())
		else:
			with open(f"{options['resynthesis_dir']}/{block_files[block_num]}", 
				"r") as qasm:
				circ = OPENQASM2Language().decode(qasm.read())
		
		# Get physical graph
		with open(options["coupling_map"], "rb") as graph:
			physical = pickle.load(graph)
		pgraph = Graph()
		pgraph.add_edges_from(physical)

		# Get hybrid graph
		with open(f"{options['subtopology_dir']}/{sub_files[block_num]}", 
			"rb") as graph:
			hybrid = pickle.load(graph)
		
		collect_stats(
			circ,
			pgraph,
			hybrid,
			structure[block_num],
			options = options,
		)
	if resynthesized:
		string = "REPLACE-\n"
	elif post_stats:
		string = "POST-\n"
	else:
		string = "PRE-\n"

	string += (
		f"    direct ops      : {options['direct_ops']}\n"
		f"    indirect ops    : {options['indirect_ops']}\n"
		f"    external ops    : {options['external_ops']}\n"
	)
	if post_stats:
		string += get_mapping_results(options)
	elif resynthesized:
		string += get_remapping_results(options)
	else:
		string += get_original_count(options)
	return string

def select_kernel(
	circuit_file : str, 
	qudit_group : Sequence[int],
	options : dict[str],
) -> Graph | None:
	if options["topology"] == "mesh":
		return select_mesh_kernel(circuit_file, qudit_group, options)
	elif options["topology"] == "falcon":
		return select_falcon_kernel(circuit_file, qudit_group, options)
	else:
		return select_linear_kernel(circuit_file, qudit_group, options)