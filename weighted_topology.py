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
) -> Graph | None:
	# Convert the physical topology to a networkx graph
	circuit = load_block_circuit(circuit_file, options)
	logical_ops = get_logical_operations(circuit)
	op_set = set(logical_ops)
	freqs = get_frequencies(circuit)
	return best_line_kernel(op_set, freqs)


def select_falcon_kernel(
	circuit_file : str, 
	qudit_group : Sequence[int],
	options : dict[str],
) -> Graph | None:
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
	elif options["blocksize"] > 4:
		raise RuntimeError(
			"Only blocksizes up to 4 are currently supported."
		)

	# Convert the physical topology to a networkx graph
	circuit = load_block_circuit(circuit_file, options)
	logical_ops = get_logical_operations(circuit)
	op_set = set(logical_ops)
	freqs = get_frequencies(circuit)

	vertex_uses = get_num_vertex_uses(logical_ops, len(qudit_group))
	vertex_degrees = get_num_vertex_uses(op_set, len(qudit_group))

	# Handle the case where there are no multi-qubit gates
	if len(op_set) == 0:
		return []
	# TODO: Generalize kernel selection for blocksizes > 4
	# Return linear 3 graph, with most used qudit in center
	if len(qudit_group) == 2 or len(qudit_group) == 3:
		return list(op_set)
	elif len(qudit_group) == 4:
		number_edges = len(op_set)
		# If there are 2 edges and 4 active qudits, then they are disjoint,
		# just return the edges that are already used. This should not happen
		# with the greedy partitioner.
		if number_edges == 2:
			return list(op_set)
		# If there are 3 edges an 4 active qudits, we can have a star or a line.
		# If a vertex has degree 3, we have a star, else we have a line.
		elif number_edges == 3:
			if max(vertex_degrees.keys(), key=lambda x: vertex_degrees[x]) == 3:
				return best_star_kernel(vertex_uses)
			# Order the edges so that the most frequent ones are first, this should
			# be achieved by keeping the original ordering of the logical ops
			else:
				return list(op_set)
		# If there are 4 edges, we can have a ring or a dipper. Based off tests run,
		# we should just return a ring in this scenario. Because this uses the 
		# falcon topology, we instead have to return a line or star. Tests show 
		# that lines tend to be better.
		elif number_edges == 4:
			return best_line_kernel(op_set, freqs)

		# If there are 5 edges, We have a ring with a bridge. Tests show that if 
		# there is a vertex that is used more than the others (by about 3), then
		# we should select a star. Otherwise select a ring. Add edges based on
		# their frequencies.
		elif number_edges == 5:
			v_uses_list = sorted(vertex_uses.values(), reverse=True)
			if v_uses_list[0] - 3 >= v_uses_list[1]:
				return best_star_kernel(vertex_uses)
			else:
				return best_line_kernel(op_set, freqs)
		# We have K_4
		# Return a ring
		else:
			return best_line_kernel(op_set, freqs)

def select_mesh_kernel(
	circuit_file : str, 
	qudit_group : Sequence[int],
	options : dict[str],
) -> Graph | None:
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
	elif options["blocksize"] > 4:
		raise RuntimeError(
			"Only blocksizes up to 4 are currently supported."
		)

	# Convert the physical topology to a networkx graph
	circuit = load_block_circuit(circuit_file, options)
	logical_ops = get_logical_operations(circuit)
	op_set = set(logical_ops)
	freqs = get_frequencies(circuit)

	vertex_uses = get_num_vertex_uses(logical_ops, len(qudit_group))
	vertex_degrees = get_num_vertex_uses(op_set, len(qudit_group))

	# Handle the case where there are no multi-qubit gates
	if len(op_set) == 0:
		return []
	# TODO: Generalize kernel selection for blocksizes > 4
	# Return linear 3 graph, with most used qudit in center
	if len(qudit_group) == 2 or len(qudit_group) == 3:
		return list(op_set)
	elif len(qudit_group) == 4:
		number_edges = len(op_set)
		# If there are 2 edges and 4 active qudits, then they are disjoint,
		# just return the edges that are already used. This should not happen
		# with the greedy partitioner.
		if number_edges == 2:
			return list(op_set)
		# If there are 3 edges an 4 active qudits, we can have a star or a line.
		# If a vertex has degree 3, we have a star, else we have a line.
		elif number_edges == 3:
			if max(vertex_degrees.keys(), key=lambda x: vertex_degrees[x]) == 3:
				return best_star_kernel(vertex_uses)
			# Order the edges so that the most frequent ones are first, this should
			# be achieved by keeping the original ordering of the logical ops
			else:
				return list(op_set)
		# If there are 4 edges, we can have a ring or a dipper. Based off tests run,
		# we should just return a ring in this scenario.
		elif number_edges == 4:
			return best_ring_kernel(op_set, freqs)

		# If there are 5 edges, We have a ring with a bridge. Tests show that if 
		# there is a vertex that is used more than the others (by about 3), then
		# we should select a star. Otherwise select a ring. Add edges based on
		# their frequencies.
		elif number_edges == 5:
			v_uses_list = sorted(vertex_uses.values(), reverse=True)
			if v_uses_list[0] - 3 >= v_uses_list[1]:
				return best_star_kernel(vertex_uses)
			else:
				return best_ring_kernel(op_set, freqs)
		# We have K_4
		# Return a ring
		else:
			return best_ring_kernel(op_set, freqs)


def run_stats(
	options : dict[str, Any],
	post_stats : bool = False,
	resynthesized : bool = False,
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

	## Run collect_stats on each block
	#for block_num in range(len(block_files)):
	#	# Get BQSKIT circuit
	#	if not post_stats:
	#		with open(f"{options['partition_dir']}/{block_files[block_num]}", 
	#			"r") as qasm:
	#			circ = OPENQASM2Language().decode(qasm.read())
	#	elif not resynthesized:
	#		with open(f"{options['synthesis_dir']}/{block_files[block_num]}", 
	#			"r") as qasm:
	#			circ = OPENQASM2Language().decode(qasm.read())
	#	else:
	#		with open(f"{options['resynthesis_dir']}/{block_files[block_num]}", 
	#			"r") as qasm:
	#			circ = OPENQASM2Language().decode(qasm.read())
	#	
	#	# Get physical graph
	#	with open(options["coupling_map"], "rb") as graph:
	#		physical = pickle.load(graph)
	#	pgraph = Graph()
	#	pgraph.add_edges_from(physical)

	#	# Get hybrid graph
	#	with open(f"{options['subtopology_dir']}/{sub_files[block_num]}", 
	#		"rb") as graph:
	#		hybrid = pickle.load(graph)
	#	
	#	collect_stats(
	#		circ,
	#		pgraph,
	#		hybrid,
	#		structure[block_num],
	#		options = options,
	#	)
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
	if options["coupling_map"] == "mesh":
		return select_mesh_kernel(circuit_file, qudit_group, options)
	elif options["coupling_map"] == "falcon" or options["coupling_map"] == "sycamore":
		return select_falcon_kernel(circuit_file, qudit_group, options)
	else:
		return select_linear_kernel(circuit_file, qudit_group, options)