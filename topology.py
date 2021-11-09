"""
Takes a circuit (qasm file) and a physical topology and produces a hybrid 
logical-physical topology.
"""
from __future__ import annotations
import pickle
from posix import listdir
from typing import Any, Dict, Sequence, Tuple
from re import match, findall

from bqskit.ir.lang.qasm2.qasm2 import OPENQASM2Language

from util import get_mapping_results, get_original_count, get_remapping_results, load_block_circuit, load_block_topology
from networkx import Graph, shortest_path_length
import networkx
from bqskit import Circuit
from statistics import mean
from itertools import permutations


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
			# TODO: handle multi qubit gates > size 2
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


def possible_kernel_names(num_qudits, top_name) -> list[str]:
	names = ["empty"]

	if num_qudits >= 2:
		names.extend(["2-line"])

	if num_qudits >= 3:
		names.extend(["2-line", "3-line"])

	if top_name == "mesh" and num_qudits >= 4:
		names.extend(["4-line", "2-2-discon", "4-star", "4-ring"])
	elif top_name == "falcon" and num_qudits >= 4:
		names.extend(["4-line", "2-2-discon", "4-star"])
	elif top_name == "linear" and num_qudits >= 4:
		names.extend(["4-line", "2-2-discon"])

	if top_name == "mesh" and num_qudits >= 5:
		names.extend(["2-3-discon", "5-star", "5-tee", "5-line", "5-dipper"])
	elif top_name == "falcon" and num_qudits >= 5:
		names.extend(["2-3-discon", "5-tee", "5-line"])
	elif top_name == "linear" and num_qudits >= 5:
		names.extend(["2-3-discon", "5-line"])
	return names


def kernel_type(kernel_edges, num_qudits) -> str:
	kernel_name = "unknown"
	degrees = get_num_vertex_uses(kernel_edges, num_qudits)
	deg_list = sorted(list(degrees.values()))

	# 2-line: only one with 1 edge
	if len(kernel_edges) == 0:
		kernel_name = "empty"
	elif len(kernel_edges) == 1:
		kernel_name = "2-line"
	elif num_qudits == 3:
		# 3-line: 2 edges and 3 distinct qubits
		# 2-discon: 2 disconnected 2-lines, 2 edges and 4 distinct qubits
		if len(kernel_edges) == 2: 
			if deg_list[0] == 1 and deg_list[1] == 1 and deg_list[2] == 2:
				kernel_name = "3-line"
	elif num_qudits == 4:
		# 3-line: 2 edges and 3 distinct qubits
		# 2-discon: 2 disconnected 2-lines, 2 edges and 4 distinct qubits
		if len(kernel_edges) == 2: 
			if deg_list[0] == 0 and all([deg_list[i] > 0 for i in range(1,4)]):
				kernel_name = "3-line"
			if all([deg_list[i] == 1 for i in range(0,4)]):
				kernel_name = "2-2-discon"
		# 4-star: 3 edges, one vertex with degree 3
		# 4-line: 3 edges, degrees 1,1,2,2
		elif len(kernel_edges) == 3:
			if deg_list[3] == 3:
				kernel_name = "4-star"
			if deg_list[0] == deg_list[1] == 1 and deg_list[2] == deg_list[3] == 2:
				kernel_name = "4-line"
		# 4-ring: 4 edges
		elif len(kernel_edges) == 4:
			kernel_name = "4-ring"
	elif num_qudits == 5:
		# 2-3-discon
		if len(kernel_edges) == 3:
			kernel_name = "2-3-discon"
		# 5-line, 5-tee, 5-star
		elif len(kernel_edges) == 4:
			if max(deg_list) == 4:
				kernel_name = "5-star"
			elif max(deg_list) == 3:
				kernel_name = "5-tee"
			else:
				kernel_name = "5-line"
		# 5-dipper
		elif len(kernel_edges) == 5:
			kernel_name = "5-dipper"

	return kernel_name


def collect_stats(
	qudit_group : Sequence[int],
	block_dir   : str,
	block_name  : str,
	blocksize   : int,
	options     : dict[str, Any],
) -> Sequence:
	"""
	Given a circuit name/directory and a block number, determine:
		Number of active qudits
		Block size
			CNOT count
			Block depth
		Kernel type
		Matching score
	"""
	blocksize = len(qudit_group) if blocksize is None else blocksize
	subcircuit = load_block_circuit(f"{block_dir}/{block_name}", options)
	kernel_path = f"{block_name.split('.qasm')[0]}_kernel.pickle"
	kernel = load_block_topology(f"{options['subtopology_dir']}/{kernel_path}")

	active_qudits = subcircuit.active_qudits
	logical_ops = get_logical_operations(subcircuit, qudit_group)
	kernel_name = kernel_type(kernel, len(qudit_group))

	return (
		len(active_qudits), 
		len(logical_ops),
		subcircuit.depth,
		kernel_name,
		kernel_score_function(kernel, logical_ops),
	)


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


def construct_permuted_kernel(
	edge_list    : Sequence[tuple[int]],
	vertex_order : Sequence[int],
) -> Sequence[tuple[int]]:
	"""
	Helper for getting all permutations of a kernel type.
	"""
	return [
		(
			min(vertex_order[u], vertex_order[v]), 
			max(vertex_order[u], vertex_order[v])
		) for (u,v) in edge_list
	]


def match_kernel(
	circuit_file : str, 
	qudit_group : Sequence[int],
	options : dict[str],
) -> Sequence[Sequence[tuple[int]]]:
	"""
	Lines
		line-cap, line-cup, line-ce, line-ec, line-ze, line-ez, line-ne, 
		line-en, line-tx, line-bx, line-lx, line-rx
	Rings
		ring, bowtie, hourglass
	Stars
		star-tl, star-br, star-tr, star-bl
	"""
	if options["blocksize"] > 5:
		raise RuntimeError(
			"Only blocksizes up to 5 are currently supported."
		)

	circuit = load_block_circuit(circuit_file, options)
	logical_ops = get_logical_operations(circuit)
	num_qudits = len(qudit_group)

	# handle the only 1-qubit gates case to avoid trying all options
	if len(logical_ops) == 0:
		return []

	if num_qudits == 2:
		# 2-line
		templates = [
			[(0,1)],
		]

	elif num_qudits == 3:
		# 3-line
		templates = [
			[(0,1), (1,2)],
		]
		
	elif num_qudits == 4:
		# 2-2-discon, 4-line, 4-ring, 4-star
		if options['topology'] == "mesh":
			templates = [
				[(0,1), (2,3)],
				[(0,1), (1,2), (2,3)], 
				[(0,1), (1,2), (2,3), (0,3)],
				[(0,1), (0,2), (0,3)],
			]
		# 2-2-discon, 4-line, 4-star
		elif options['topology'] == "falcon":
			templates = [
				[(0,1), (2,3)],
				[(0,1), (1,2), (2,3)], 
				[(0,1), (0,2), (0,3)],
			]
		# 2-2-discon, 4-line, 4-star
		elif options['topology'] == "linear":
			templates = [
				[(0,1), (2,3)],
				[(0,1), (1,2), (2,3)], 
			]

	elif num_qudits == 5:
		# 2-3-discon, 5-line, 5-tee, 5-dipper, 5-star
		if options['topology'] == "mesh":
			templates = [
				[(0,1), (2,3), (3,4)],
				[(0,1), (1,2), (2,3), (3,4)],
				[(0,1), (1,2), (1,3), (3,4)],
				[(0,1), (1,2), (2,3), (0,3), (0,4)],
				[(0,1), (0,2), (0,3), (0,4)],
			]
		# 2-3-discon, 5-line, 5-tee
		elif options['topology'] == "falcon":
			templates = [
				[(0,1), (2,3), (3,4)],
				[(0,1), (1,2), (2,3), (3,4)],
				[(0,1), (1,2), (1,3), (3,4)],
			]
		# 2-3-discon, 5-line
		elif options['topology'] == "linear":
			templates = [
				[(0,1), (2,3), (3,4)],
				[(0,1), (1,2), (2,3), (3,4)],
			]

	vertex_list  = list(range(num_qudits))
	vertex_perms = list(permutations(vertex_list, num_qudits))
	best_kernel = []
	best_score  = 0
	for template in templates:
		for perm in vertex_perms:
			permuted_kernel = construct_permuted_kernel(template, perm)
			edge_score, node_score = kernel_score_function(logical_ops, permuted_kernel)
			#if edge_score + node_score > best_score:
			if edge_score > best_score:
				best_kernel = permuted_kernel
				best_score = edge_score

	return best_kernel


def kernel_score_function(
	logical_ops : Sequence[tuple[int]], 
	kernel_edges : Sequence[tuple[int]],
) -> tuple[int]:
	"""
	Return the "edge score" and "node score" of the kernel passed.
	"""
	edge_score = sum([
		logical_ops.count((u,v)) + logical_ops.count((v,u)) 
		for (u,v) in kernel_edges
	])

	vertices = list(set([u for (u,v) in kernel_edges] + [v for (u,v) in kernel_edges]))
	op_occurances = [u for (u,v) in logical_ops] + [v for (u,v) in logical_ops]
	kern_occurances = [u for (u,v) in kernel_edges] + [v for (u,v) in kernel_edges]

	op_values     = {n: 0 for n in vertices}
	kernel_values = {n: 0 for n in vertices} 
	for v in vertices:
		op_values[v]     = op_occurances.count(v)
		kernel_values[v] = kern_occurances.count(v)
	
	node_score = 0
	for x in vertices:
		node_score += op_values[x] * kernel_values[x]

	return (edge_score, node_score)


def edge_score_function(
	logical_ops  : Sequence[tuple[int]], 
	kernel_edges : Sequence[tuple[int]],
) -> tuple[int]:
	"""
	Return the "edge score" of the passed kernel. The edge score appears to be
	a better predictor of average and minimum cnot and depth for partitions.

	Arguments:
		logical_ops (Sequence[tuple[int]]): List of edges that appear in the 
			partition where edge counts correspond to the number of operations
			of that kind in the partition.

		kernel_edges (Sequence[tuple[int]]): Edges in the kernel graph.

	Returns:
		score (int): inner product between logical ops edge frequency vector
			and the kernel_edges indicator vector.
	"""
	score = 0
	for (u,v) in kernel_edges:
		score += logical_ops.count((u,v))
		score += logical_ops.count((v,u))
	return score


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
		block_dir = options["partition_dir"]
		block_files = listdir(block_dir)
		block_files.remove(f"structure.pickle")
	else:
		if not resynthesized:
			block_dir = options["synthesis_dir"]
			blocks = listdir(options["synthesis_dir"])
		else:
			block_dir = options["resynthesis_dir"]
			blocks = listdir(options["resynthesis_dir"])
		block_files = []
		for bf in blocks:
			if bf.endswith(".qasm"):
				block_files.append(bf)
	block_files = sorted(block_files)

	# Get the qudit group
	with open(f"{options['partition_dir']}/structure.pickle", "rb") as f:
		structure = pickle.load(f)

	active_qudits_list = []
	cnots_list  = []
	depth_list  = []
	edge_score_list  = []
	node_score_list  = []
	names = possible_kernel_names(options["blocksize"], options["topology"])
	kernel_dict = {k:0 for k in names}
	kernel_coverage = {k:0 for k in names}

	# Run collect_stats on each block
	for block_num in range(len(block_files)):
		(num_active, cnots, depth, kernel_name, score) = collect_stats(
			qudit_group=structure[block_num],
			block_dir=block_dir,
			block_name=block_files[block_num],
			blocksize=options["blocksize"],
			options=options
		)
		active_qudits_list.append(num_active)
		cnots_list.append(cnots)
		depth_list.append(depth)
		edge_score_list.append(score[0])
		node_score_list.append(score[1])
		kernel_dict[kernel_name] += 1
		kernel_coverage[kernel_name] += cnots
	total_cnots = sum(cnots_list)
	for name in names:
		kernel_coverage[name] /= total_cnots
		
	if resynthesized:
		string = "REPLACE-\n"
	elif post_stats:
		string = "POST-\n"
	else:
		string = "PRE-\n"

	string += (
		f"Total CNOTs: {sum(cnots_list)}\n"
		f"Total matching edge score: {sum(edge_score_list)}\n"
		f"Total matching node score: {sum(node_score_list)}\n"
		f"Average CNOTs: {format(mean(cnots_list), '.3f')}\n"
		f"Average depth: {format(mean(depth_list), '.3f')}\n"
		f"Average edge score: {format(mean(edge_score_list), '.3f')}\n"
		f"Average node score: {format(mean(node_score_list), '.3f')}\n"
	)
	if post_stats:
		string += get_mapping_results(options)
	elif resynthesized:
		string += get_remapping_results(options)
	else:
		string += f"Kernel counts:\n"
		for k in sorted(list(kernel_dict.keys())):
			coverage = format(kernel_coverage[k] * 100, '.1f')
			string += f"  {k}: {kernel_dict[k]} ({coverage}%)\n"
		string += get_original_count(options)
	return string
