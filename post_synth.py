import argparse
import math
import pickle
import re
import networkx as nx
from weighted_topology import check_multi, collect_stats, get_logical_operations, is_same
from bqskit.ir.lang.qasm2.qasm2 import OPENQASM2Language
from posix import listdir


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
		
	# Load qudit groups
	with open(f"{block_path}/structure.pickle", "rb") as f:
		structure = pickle.load(f)
	log_ops = []

	for i in range(len(tops)):
		# load hybrid graph
		with open(f"{topo_path}/{tops[i]}", "rb") as f:
			hybrid = pickle.load(f)

		# load circuit
		with open(f"{synth_path}/{circs[i]}", "r") as f:
			circuit = OPENQASM2Language().decode(f.read())

		# block name and number
		group = structure[i]

		log_ops.append(get_logical_operations(circuit, group))

		stats = collect_stats(circuit, physical, hybrid, group)
		print(f"BLOCK {i}")
		print(stats)
	
	num_q_sqrt = int(re.search("\d+", map_type)[0])
	num_q = num_q_sqrt ** 2
	mapping = {k:k for k in range(num_q)}
	swap_counts  = {k:0 for k in range(len(tops))}
	swap_lists = [[] for _ in range(num_q)]
	counted_swaps = []
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
			for block in range(len(tops)):
				for log_op in log_ops[block]:
					if is_same(v_op, log_op):
						# Find the number of SWAPs to count
						if not no_counts[p_op[0]] == p_op[1]:
							swaps_to_count = len(swap_lists[p_op[0]]) + len(swap_lists[p_op[1]]) 
							swap_counts[block] += swaps_to_count

							swaps_to_remove = []
							if swaps_to_count > 0:
								swaps_to_remove.extend(swap_lists[p_op[0]])
								swaps_to_remove.extend(swap_lists[p_op[1]])
							if len(swaps_to_remove) > 0:
								swap_lists[p_op[0]] = []
								swap_lists[p_op[1]] = []
								for qudit in range(num_q):
									for s in swap_lists[qudit]:
										if s in swaps_to_remove:
											swap_lists[qudit].remove(s)
						log_ops[block].remove(log_op)
						break_flag = True
						break
				if break_flag:
					break
	
	for block in range(len(tops)):
		print(f"BLOCK {block}")
		print(swap_counts[block])