import argparse
from genericpath import exists

from networkx.drawing import layout
from mapping import do_routing
import math
import pickle
import re
import networkx as nx
from weighted_topology import check_multi, collect_stats_tuples, get_logical_operations, is_same
from bqskit.ir.lang.qasm2.qasm2 import OPENQASM2Language
from posix import listdir


def count_swaps(mapped_path, mapping, num_q, topologies, logical_ops):

	swap_counts  = {k:0 for k in range(len(topologies))}
	swap_lists = [[] for _ in range(num_q)]
	no_counts = {k:-1 for k in range(num_q)}

	mapped_operations = []
	with open(mapped_path, "r") as f:
		for line in f:
			if (p_op := check_multi(line)) is not None:
				mapped_operations.append(line)

	swaps = 0
	for mapped_op in mapped_operations:
		# SWAP
		p_op = check_multi(mapped_op)
		if str(mapped_op).startswith("swap"):
			# Mark off interactions that shouldn't impact swap count
			no_counts[p_op[0]] = p_op[1]
			no_counts[p_op[1]] = p_op[0]
			# Keep track of swaps
			swap_lists[p_op[0]].append(swaps)
			swap_lists[p_op[1]].append(swaps)
			swaps += 1
			# Do swap
			temp = mapping[p_op[0]]
			mapping[p_op[0]] = mapping[p_op[1]]
			mapping[p_op[1]] = temp
		# CNOT
		else:
			v_op = (mapping[p_op[0]], mapping[p_op[1]])

			break_flag = False
			for block in range(len(topologies)):
				for log_op in logical_ops[block]:
					if is_same(v_op, log_op):
						# Find the number of SWAPs to count
						if not no_counts[p_op[0]] == p_op[1]:
							a = set(swap_lists[p_op[0]])
							b = set(swap_lists[p_op[1]])
							swaps_to_remove = a.union(b)
							swaps_to_count = len(swaps_to_remove)
							swap_counts[block] += swaps_to_count

							swap_lists[p_op[0]] = []
							swap_lists[p_op[1]] = []

							for old_swap in list(swaps_to_remove):
								for qudit in range(len(swap_lists)):
									if old_swap in swap_lists[qudit]:
										swap_lists[qudit].remove(old_swap)
						logical_ops[block].remove(log_op)
						break_flag = True
						break
				if break_flag:
					break

#	print(swaps)
#	s = 0
#	for i in range(len(topologies)):
#		s += swap_counts[i]
#	print(s)
#	for a in swap_lists:
#		if len(a) > 0:
#			print(a)
	return swap_counts


def count_stats(
	topologies, topology_path,
	blocks, block_path,
	synthblocks, synth_path,
	structure, physical_graph
):
	pre_stats = []
	post_stats = []
	sub_stats = []
	logical_ops = []
	for i in range(len(topologies)):
		# load hybrid graph
		with open(f"{topology_path}/{topologies[i]}", "rb") as f:
			hybrid = pickle.load(f)

		# load pre synth circuit
		with open(f"{block_path}/{blocks[i]}", "r") as f:
			block = OPENQASM2Language().decode(f.read())

		# load post synth circuit
		with open(f"{synth_path}/{synthblocks[i]}", "r") as f:
			circuit = OPENQASM2Language().decode(f.read())

		# block name and number
		group = structure[i]

		logical_ops.append(get_logical_operations(circuit, group))

		pre, _ = collect_stats_tuples(block, physical_graph, hybrid, group)
		post, sub = collect_stats_tuples(circuit, physical_graph, hybrid, group)
		pre_stats.append(pre)
		post_stats.append(post)
		sub_stats.append(sub)

	return pre_stats, post_stats, sub_stats, logical_ops


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument(
		"synthesis_files_dir", type=str,
		default="subtopology_files/add_9_mesh_3_3_blocksize_4_custom_nearest-physical",
		help="synthesis qasm",
	)
	args = parser.parse_args()

	schemes = ["_shortest-path", "_nearest-physical", "_mst-path", "_mst-density"]
	edge_scheme = ""
	for scheme in schemes:
		if scheme in args.synthesis_files_dir:
			edge_scheme = scheme

	full_name  = args.synthesis_files_dir.split("/")[-1]
	short_name = full_name.split(edge_scheme)[0]
	block_path = f"block_files/{short_name}"
	synth_path = f"synthesis_files/{full_name}"
	topo_path = f"subtopology_files/{full_name}"
	mapped_path = f"mapped_qasm/{full_name}"

	# load physical graph
	map_type = re.search("mesh_\d+_\d+", short_name)[0]
	coupling_map = f"coupling_maps/{map_type}"
	with open(coupling_map, "rb") as f:
		edge_set = pickle.load(f)
	physical = nx.Graph()
	physical.add_edges_from(edge_set)

	tops = sorted(listdir(topo_path))
	tops.remove("summary.txt")
	circs = sorted(listdir(synth_path))
	for c in circs:
		if ".qasm" not in c:
			circs.remove(c)
	blocks = sorted(listdir(block_path))
	blocks.remove("structure.pickle")

	# Load qudit groups
	with open(f"{block_path}/structure.pickle", "rb") as f:
		structure = pickle.load(f)

	num_q_sqrt = int(re.search("\d+", map_type)[0])
	num_q = num_q_sqrt ** 2
	mapping = {k:k for k in range(num_q)}

	pre_stats, post_stats, sub_stats, logical_ops = count_stats(
		tops, topo_path,
		blocks, block_path,
		circs, synth_path,
		structure, physical,
	)
	swap_counts = count_swaps(mapped_path, mapping, num_q, tops, logical_ops)

	# Get the "unsynthesized" numbers
	# route the original circuit without synthesizing
	mapped_nosynth_path = f"mapped_qasm/{short_name}_nosynth"
	if not exists(f"mapped_qasm/{short_name}_nosynth"):
		if "greedy" in short_name:
			shortest_name = short_name.split("_greedy")[0]
		else:
			shortest_name = short_name
		do_routing(
			f"layout_qasm/{shortest_name}",
			coupling_map,
			mapped_nosynth_path
		)

	logical_ops_nosynth = []
	mapping = {k:k for k in range(num_q)}
	_, post_nosynth, sub_nosynth, logical_ops_nosynth = count_stats(
		tops, topo_path,
		blocks, block_path,
		blocks, block_path,
		structure, physical,
	)
	swaps_nosynth = count_swaps(mapped_nosynth_path, mapping, num_q, tops,
		logical_ops_nosynth)

	# for each block file
	# append to a circuit
	# get a breakdown of cnots and swaps per block

	for i in range(len(tops)):
		line = ""
		# block number
		line += f"{i}, "

		## Pre synth
		# 0 active qudits
		line += f"{pre_stats[i][0]}, "
		# 1 direct ops
		line += f"{pre_stats[i][1]}, "
		# 2 indirect ops
		line += f"{pre_stats[i][2]}, "
		# 3 indirect volume
		line += f"{pre_stats[i][3]}, "
		# 4 internal volume
		line += f"{pre_stats[i][4]}, "
		# 5 external ops
		line += f"{pre_stats[i][5]}, "
		# 6 external volume
		line += f"{pre_stats[i][6]}, "
		# 7 total volume
		line += f"{pre_stats[i][7]}, "
		# 8 cnot count
		line += f"{pre_stats[i][8]}, "
		# unsynthed cnot count
		line += f"{post_nosynth[i][8] + 3*swaps_nosynth[i]}, "

		## Post synth
		# 1 direct ops
		line += f"{post_stats[i][1]}, "
		# 5 external ops
		line += f"{post_stats[i][5]}, "
		# 6 external volume
		line += f"{post_stats[i][6]}, "
		# 8 cnot count
		line += f"{post_stats[i][8]}, "

		# swap count
		line += f"{swap_counts[i]}, "
		# total cnots
		line += f"{post_stats[i][8] + 3*swap_counts[i]}, "

		## Subtopology
		# 0 number of edges
		line += f"{sub_stats[i][0]}, "
		# 1 physical edges
		line += f"{sub_stats[i][1]}, "
		# 2 logical edges
		line += f"{sub_stats[i][2]}, "
		# 3 edge path sum
		line += f"{sub_stats[i][3]}"

		print(line)

	cx = 0
	swap = 0
	origcx = 0
	origswap = 0
	for i in range(len(tops)):
		cx += post_stats[i][8]
		swap += swap_counts[i]
		origcx += post_nosynth[i][8]
		origswap += swaps_nosynth[i]
	print(f"Original cx: {origcx}")
	print(f"Original swaps: {origswap}")
	print(f"Flow cx: {cx}")
	print(f"Flow swaps: {swap}")

	print(f"Original total: {origcx + 3* origswap}")
	print(f"Flow total: {cx + 3* swap}")