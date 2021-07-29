import argparse
import math
import pickle
import re
import networkx as nx
from weighted_topology import collect_stats
from bqskit.ir.lang.qasm2.qasm2 import OPENQASM2Language


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("block_dir", type=str, help="block files dir")
	parser.add_argument("subtopology_path", type=str, help="graphs of subtop")
	parser.add_argument("synthesized_path", type=str, help="synthesis qasm")
	args = parser.parse_args()


	# load circuit
	with open(f"{args.synthesized_path}", "r") as f:
		circuit = OPENQASM2Language().decode(f.read())
	
	# load physical graph
	map_type = re.search("mesh_\d+_\d+", args.block_dir)[0]
	coupling_map = f"coupling_maps/{map_type}"
	with open(coupling_map, "rb") as f:
		edge_set = pickle.load(f)
	physical = nx.Graph()
	physical.add_edges_from(edge_set)
	
	# load hybrid graph
	with open(args.subtopology_path, "rb") as f:
		hybrid = pickle.load(f)
	
	# Load qudit group
	with open(f"{args.block_dir}/structure.pickle", "rb") as f:
		structure = pickle.load(f)
	# block name and number
	name = str(args.subtopology_path.split("_subtopology")[0].split("/")[-1])
	number = int(re.search("\d+", name)[0])
	group = structure[number]

	stats = collect_stats(circuit, physical, hybrid, group)
	print(stats)
