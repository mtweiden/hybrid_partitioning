from __future__ import annotations

from sys import argv
from os import listdir
from pickle import load, dump
from topology import kernel_score_function, get_logical_operations, construct_permuted_kernel
from util import load_block_circuit
from itertools import permutations
import argparse


def match_kernel(
	circuit_file : str, 
	qudit_group : Sequence[int],
	options : dict[str],
) -> Sequence[Sequence[tuple[int]]]:
	"""
	Valid template categories are:
		blocksize 3:
			lines, alls
		blocksize 4:
			lines, stars, rings, alls, embedded, trees,
			kites, thetas
		blocksize 5:
			lines, stars, tees, dippers, alls, embedded, trees
	
	NOTE: embedded means embedded in a 2D nearest neighbor mesh
	"""

	if options["blocksize"] > 5:
		raise RuntimeError(
			"Only blocksizes up to 5 are currently supported."
		)
	line_2 = [(0,1)]
	line_3 = [(0,1), (1,2)]
	line_4 = [(0,1), (1,2), (2,3)]
	line_5 = [(0,1), (1,2), (2,3), (3,4)]
	alls_3 = [(0,1), (0,2), (1,2)]
	alls_4 = [(0,1), (0,2), (0,3), (1,2), (1,3), (2,3)]
	alls_5 = [(0,1), (0,2), (0,3), (0,4), (1,2), (1,3), (1,4), (2,3), (2,4), (3,4)]
	ring_4 = [(0,1), (1,2), (2,3), (0,3)]
	star_4 = [(0,1), (0,2), (0,3)]
	kite_4 = [(0,1), (1,2), (2,3), (1,3)]
	theta_4 = [(0,1), (1,2), (2,3), (0,3), (1,3)]
	star_5 = [(0,1), (0,2), (0,3), (0,4)]
	dipper = [(0,1), (1,2), (2,3), (0,3), (0,4)]
	tees_5 = [(0,1), (1,2), (1,3), (3,4)]

	circuit = load_block_circuit(circuit_file, options)
	logical_ops = get_logical_operations(circuit)
	num_qubits = len(qudit_group)

	templates = []

	if num_qubits < 2:
		templates = []
	elif num_qubits == 2:
		templates = [line_2]
	elif num_qubits == 3:
		if options['category'] in ("lines", "stars", "rings", "kites", "thetas"):
			templates = [line_3]
		elif options['category'] == "alls":
			templates = [alls_3]
		else:
			raise RuntimeError(f"Unrecognized options['category'] {options['category']}")
	elif num_qubits == 4:
		if options['category'] == "lines":
			templates = [line_4]
		elif options['category'] == "stars":
			templates = [star_4]
		elif options['category'] == "rings":
			templates = [ring_4]
		elif options['category'] == "alls":
			templates = [alls_4]
		elif options['category'] == "kites":
			templates = [kite_4]
		elif options['category'] == "thetas":
			templates = [theta_4]
		elif options['category'] == "embedded":
			templates = [line_4, star_4, ring_4]
		elif options['category'] == "trees":
			templates = [line_4, star_4]
		else:
			raise RuntimeError(f"Unrecognized options['category'] {options['category']}")
	elif num_qubits == 5:
		if options['category'] == "lines":
			templates = [line_5]
		elif options['category'] == "stars":
			templates = [star_5]
		elif options['category'] == "tees":
			templates = [tees_5]
		elif options['category'] == "dippers":
			templates = [tees_5]
		elif options['category'] == "alls":
			templates = [alls_5]
		elif options['category'] == "embedded":
			templates = [line_5, star_5, tees_5, dipper]
		elif options['category'] == "trees":
			templates = [line_5, star_5, tees_5]
		else:
			raise RuntimeError(f"Unrecognized options['category'] {options['category']}")
	else:
		raise RuntimeError("Only upto 5 qubits blocks supported.")

	vertex_list  = list(range(num_qubits))
	vertex_perms = list(permutations(vertex_list, num_qubits))
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


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("block_dir", type=str) 
	parser.add_argument("valid_subtopologies", type=str, default="embedded") 
	args = parser.parse_args()
	block_dir = args.block_dir

	blocks = sorted(listdir(block_dir))
	blocks.remove("structure.pickle")

	with open(f"{block_dir}/structure.pickle", "rb") as f:
		structure = load(f)

	options = {
		"blocksize" : 4,
		"category"  : args.valid_subtopologies,
		"checkpoint_as_qasm": True,
	}

	for i, block in enumerate(blocks):
		block_path = f"{block_dir}/{block}"
		name = block.split(".qasm")[0]
		if block_dir.endswith('/'):
			topo_dir = block_dir.split('/')[-2]
		else:
			topo_dir = block_dir.split('/')[-1]
		topo_path  = f"subtopology_files/{topo_dir}_kernel/{name}_kernel.pickle"
		print(topo_path)
		edges = match_kernel(
			circuit_file = block_path,
			qudit_group  = structure[i],
			options      = options,
		)
		with open(topo_path, "wb") as f:
			print(edges)
			dump(edges, f)
