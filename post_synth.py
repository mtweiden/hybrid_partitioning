from __future__ import annotations

import argparse
from genericpath import exists
from os import mkdir
from typing import Any
from bqskit.ir.circuit import Circuit

from networkx.drawing import layout
from coupling import get_coupling_map
from mapping import do_routing
import math
import pickle
import re
import networkx as nx
from weighted_topology import check_multi, collect_stats_tuples, get_logical_operations, is_same
from bqskit.ir.lang.qasm2.qasm2 import OPENQASM2Language
from posix import listdir


def count_swaps(
	mapped_path, 
	num_q, 
	num_blocks,
	logical_ops
):
	swap_counts  = {k:0 for k in range(num_blocks)}
	swap_lists = [[] for _ in range(num_q)]
	no_counts = {k:-1 for k in range(num_q)}
	mapping = {k:k for k in range(num_q)}

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
			for block in range(num_blocks):
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

	return swap_counts


def replace_blocks(
	options: dict[str, Any],
):
	topologies = sorted(listdir(options["subtopology_dir"]))
	topologies.remove("summary.txt")
	blocks = sorted(listdir(options["partition_dir"]))
	blocks.remove("structure.pickle")
	with open(f"{options['partition_dir']}/structure.pickle", "rb") as f:
		structure = pickle.load(f)
	synthblocks = sorted(listdir(options["synthesis_dir"]))
	for sb in synthblocks:
		if ".qasm" not in sb:
			synthblocks.remove(sb)
	with open(options["coupling_map"], "rb") as f:
		edge_set = pickle.load(f)
	physical_graph = nx.Graph()
	physical_graph.add_edges_from(edge_set)
	
	# Make a directory for the non-synthesized blocks
	if not exists(options["nosynth_dir"]):
		mkdir(options["nosynth_dir"])
	# Make a directory for the replaced/resynthesis blocks
	if not exists(options["resynthesis_dir"]):
		mkdir(options["resynthesis_dir"])

	# Route each block
	reroute_flag = False
	for block_num in range(len(blocks)):
		input_qasm_file = options["partition_dir"] + "/" + blocks[block_num]
		output_qasm_file = options["nosynth_dir"] + "/" + blocks[block_num]
		topology = options["subtopology_dir"] + "/" + topologies[block_num]
		if not exists(output_qasm_file):
			reroute_flag = True
			(_, coupling_graph) = get_coupling_map(topology)
			print(
				f"Routing block {block_num+1}/{len(blocks)} "
				f"with coupling map {coupling_graph}..."
			)
			# If routing cannot be done, copy over synthesized file
			synthesized_qasm_file = options["synthesis_dir"] + "/" + blocks[block_num]
			if not do_routing(input_qasm_file, topology, output_qasm_file):
				with open(output_qasm_file, "w") as out_f:
					with open(synthesized_qasm_file, "r") as in_f:
						out_f.write(in_f.read())

		# Determine whether each file would have been shorter had it been routed
		# Count cnots in synthesized
		synthesized_qasm_file = options["synthesis_dir"] + "/" + blocks[block_num]
		with open(synthesized_qasm_file, "r") as f:
			synthesized_qasm = f.read()
			cnots = re.findall("cx ", synthesized_qasm)
			swaps = re.findall("swap ", synthesized_qasm)
		synthesized_count = len(cnots) + 3 * len(swaps)
		# Count cnots & swaps in routed
		with open(output_qasm_file, "r") as f:
			routed_qasm = f.read()
			cnots = re.findall("cx ", routed_qasm)
			swaps = re.findall("swap ", routed_qasm)
		routed_count = len(cnots) + 3 * len(swaps)

		# Put the smaller block in the resynth directory
		replaced_qasm = options["resynthesis_dir"] + "/" + blocks[block_num]
		if not exists(replaced_qasm):
			with open(replaced_qasm, "w") as f:
				if synthesized_count <= routed_count:
					f.write(synthesized_qasm)
				else:
					print(
						f"  Using routed version of block {block_num} "
						f"({routed_count/synthesized_count}x smaller)"
					)
					f.write(routed_qasm)
	
	if reroute_flag:
		# Recreate new synthesized qasm file
		new_circ = Circuit(options['num_p'])
		for block_num in range(len(blocks)):
			with open(
				f"{options['resynthesis_dir']}/{blocks[block_num]}", "r"
			) as f:
				subcircuit_qasm = f.read()
			subcircuit = OPENQASM2Language().decode(subcircuit_qasm)
			group_len = subcircuit.num_qudits
			qudit_group = [structure[block_num][x] for x in range(group_len)]
			new_circ.append_circuit(subcircuit, qudit_group)
		
		with open(options["resynthesized_qasm_file"], "w") as f:
			f.write(OPENQASM2Language().encode(new_circ))

		# Route the entire circuit again
		print("="*80)
		print("Rerouting new circuit...")
		print("="*80)
		do_routing(
			options["resynthesized_qasm_file"],
			options["coupling_map"],
			options["remapped_qasm_file"]
		)


def count_stats(
	topologies, 
	topology_path,
	blocks, 
	block_path,
	synthblocks, 
	synth_path,
	structure, 
	physical_graph
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


def get_block_cnot_count(
	qasm_file: str
) -> int:
	count = 0
	with open(qasm_file, "r") as f:
		for line in f:
			if re.match("cx", line):
				count += 1
	return count


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument(
		"synthesis_files_dir", type=str,
		default="subtopology_files/add_9_mesh_3_3_blocksize_4_custom_nearest-physical",
		help="synthesis qasm",
	)
	parser.add_argument(
		"--replacement", action="store_true", help="use replacement data or original"
	)
	args = parser.parse_args()

	full_name  = args.synthesis_files_dir.split("/")[-1]
	short_name = full_name.split("_kernel")[0]
	block_path = f"block_files/{short_name}"
	topo_path = f"subtopology_files/{full_name}"
	if args.replacement:
		synth_path = f"synthesis_files/{full_name}_resynth"
		mapped_path = f"mapped_qasm/{full_name}_remapped"
	else:
		synth_path = f"synthesis_files/{full_name}"
		mapped_path = f"mapped_qasm/{full_name}"

	# load physical graph
	map_type = re.search("mesh_\d+", short_name)[0]
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

	pre_stats, post_stats, sub_stats, logical_ops = count_stats(
		tops, topo_path,
		blocks, block_path,
		circs, synth_path,
		structure, physical,
	)
	swap_counts = count_swaps(mapped_path, num_q, len(tops), logical_ops)

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
	swaps_nosynth = count_swaps(mapped_nosynth_path, num_q, len(tops),
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
		# 5 external ops
		line += f"{pre_stats[i][3]}, "
		# 8 cnot count
		line += f"{pre_stats[i][4]}, "
		# unsynthed cnot count
		line += f"{post_nosynth[i][4] + 3*swaps_nosynth[i]}, "

		## Post synth
		# 1 direct ops
		line += f"{post_stats[i][1]}, "
		# 5 external ops
		line += f"{post_stats[i][3]}, "
		# 8 cnot count
		line += f"{post_stats[i][4]}, "

		# swap count
		line += f"{swap_counts[i]}, "
		# total cnots
		line += f"{post_stats[i][4] + 3*swap_counts[i]}, "

		## Subtopology
		# 0 number of edges
		line += f"{sub_stats[i][0]}, "
		# 3 kernel name
		line += f"{sub_stats[i][1]}"

		print(line)

	cx = 0
	swap = 0
	origcx = 0
	origswap = 0
	for i in range(len(tops)):
		cx += post_stats[i][4]
		swap += swap_counts[i]
		origcx += post_nosynth[i][4]
		origswap += swaps_nosynth[i]
	print(f"Original cx: {origcx}")
	print(f"Original swaps: {origswap}")
	print(f"Flow cx: {cx}")
	print(f"Flow swaps: {swap}")

	print(f"Original total: {origcx + 3* origswap}")
	print(f"Flow total: {cx + 3* swap}")