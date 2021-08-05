import argparse
import math
import pickle
import re
import networkx as nx
from weighted_topology import collect_stats
from bqskit.ir.lang.qasm2.qasm2 import OPENQASM2Language
from posix import listdir


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("block_dir", type=str, help="block files dir")
	parser.add_argument("subtopology_path", type=str, help="graphs of subtop")
	parser.add_argument("synthesized_path", type=str, help="synthesis qasm")
	args = parser.parse_args()

	
	# load physical graph
	map_type = re.search("mesh_\d+_\d+", args.block_dir)[0]
	coupling_map = f"coupling_maps/{map_type}"
	with open(coupling_map, "rb") as f:
		edge_set = pickle.load(f)
	physical = nx.Graph()
	physical.add_edges_from(edge_set)
	
	tops = sorted(listdir(args.subtopology_path))
	tops.remove("summary.txt")
	circs = sorted(listdir(args.synthesized_path))
	for c in circs:
		if ".qasm" not in c:
			circs.remove(c)
		
	# Load qudit groups
	with open(f"{args.block_dir}/structure.pickle", "rb") as f:
		structure = pickle.load(f)

	for i in range(len(tops)):
		# load hybrid graph
		with open(f"{args.subtopology_path}/{tops[i]}", "rb") as f:
			hybrid = pickle.load(f)

		# load circuit
		with open(f"{args.synthesized_path}/{circs[i]}", "r") as f:
			circuit = OPENQASM2Language().decode(f.read())
		# block name and number
		group = structure[i]

		stats = collect_stats(circuit, physical, hybrid, group)
		print(f"BLOCK {i}")
		print(stats)
