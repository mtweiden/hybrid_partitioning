"""
Takes a circuit (qasm file) and a physical topology and produces a hybrid 
logical-physical topology.
"""
from __future__ import annotations
import pickle
from posix import listdir
from typing import Any, Dict, Sequence, Tuple
from re import match, findall

from util import get_mapping_results, get_original_count, get_remapping_results, load_block_circuit, load_block_topology
from networkx import Graph, shortest_path_length
import networkx
from bqskit import Circuit
from statistics import mean


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


def possible_kernel_names(blocksize, top_name) -> list[str]:
	if top_name == "mesh" and blocksize == 3:
		return ["empty", "2-line", "3-line"]
	if top_name == "falcon" and blocksize == 3:
		return ["empty", "2-line", "3-line"]
	if top_name == "linear" and blocksize == 3:
		return ["empty", "2-line", "3-line"]
	if top_name == "mesh" and blocksize == 4:
		return ["empty", "2-line", "3-line", "4-line", "2-discon", "4-star", "4-ring"]
	if top_name == "falcon" and blocksize == 4:
		return ["empty", "2-line", "3-line", "4-line", "2-discon", "4-star"]
	if top_name == "linear" and blocksize == 4:
		return ["empty", "2-line", "3-line", "4-line", "2-discon"]


def kernel_type(kernel_edges, blocksize) -> str:
	kernel_name = "unknown"
	degrees = get_num_vertex_uses(kernel_edges, blocksize)
	deg_list = sorted(list(degrees.values()))

	# 2-line: only one with 1 edge
	if len(kernel_edges) == 0:
		kernel_name = "empty"
	elif len(kernel_edges) == 1:
		kernel_name = "2-line"
	elif blocksize == 3:
		# 3-line: 2 edges and 3 distinct qubits
		# 2-discon: 2 disconnected 2-lines, 2 edges and 4 distinct qubits
		if len(kernel_edges) == 2: 
			if deg_list[0] == 1 and deg_list[1] == 1 and deg_list[2] == 2:
				kernel_name = "3-line"
	elif blocksize == 4:
		# 3-line: 2 edges and 3 distinct qubits
		# 2-discon: 2 disconnected 2-lines, 2 edges and 4 distinct qubits
		if len(kernel_edges) == 2: 
			if deg_list[0] == 0 and all([deg_list[i] > 0 for i in range(1,4)]):
				kernel_name = "3-line"
			if all([deg_list[i] == 1 for i in range(0,4)]):
				kernel_name = "2-discon"
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

	return kernel_name


def kernel_matching_score(
	kernel_edges  : Sequence[tuple[int]],
	logical_edges : Sequence[tuple[int]],
) -> int:
	"""
	Return the matching score defined by:
		frequency of edges in kernel - frequency of edges not in kernel
	"""
	in_kernel     = 0
	not_in_kernel = 0
	for (a,b) in logical_edges:
		if (a,b) in kernel_edges or (b,a) in kernel_edges:
			in_kernel += 1
		else:
			not_in_kernel += 1
	return in_kernel - not_in_kernel



def collect_stats(
	qudit_group : Sequence[int],
	block_dir   : str,
	block_name  : str,
	blocksize   : int,
	options     : dict[str, Any],
) -> str:
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
	kernel_name = kernel_type(kernel, blocksize)

	return (
		len(active_qudits), 
		len(logical_ops),
		subcircuit.depth,
		kernel_name,
		kernel_matching_score(kernel, logical_ops),
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
	score_list  = []
	names = possible_kernel_names(options["blocksize"], options["topology"])
	kernel_dict = { k:0 for k in names }

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
		score_list.append(score)
		kernel_dict[kernel_name] += 1
		
	if resynthesized:
		string = "REPLACE-\n"
	elif post_stats:
		string = "POST-\n"
	else:
		string = "PRE-\n"

	string += (
		f"Total Operations: {sum(cnots_list)}\n"
		f"Total matching score: {sum(score_list)}\n"
		f"Average CNOTs: {format(mean(cnots_list), '.3f')}\n"
		f"Average depth: {format(mean(depth_list), '.3f')}\n"
		f"Average score: {format(mean(score_list), '.3f')}\n"
		f"Kernel counts:\n"
	)
	for k in sorted(list(kernel_dict.keys())):
		string += f"  {k}: {kernel_dict[k]}\n"
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