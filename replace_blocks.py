from __future__ import annotations

from sys import argv
from os import listdir
from pickle import load, dump
from topology import kernel_score_function, get_logical_operations, construct_permuted_kernel
from util import load_block_circuit
from itertools import permutations


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
				[(0,1),(1,2),(2,3)],
				[(0,1),(0,2),(0,3)],
			]

	elif num_qudits == 5:
		# 2-3-discon, 5-line, 5-tee, 5-dipper, 5-star
		if options['topology'] == "mesh":
			templates = [
				[(0,1),(1,2),(2,3),(3,4)],
				[(0,1),(1,2),(1,3),(3,4)],
				[(0,1),(0,2),(0,3),(0,4)],
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


if __name__ == "__main__":
	block_dir   = argv[1]

	blocks = sorted(listdir(block_dir))
	blocks.remove("structure.pickle")

	with open(f"{block_dir}/structure.pickle", "rb") as f:
		structure = load(f)

	options = {
		"blocksize" : 4,
		"topology"  : "mesh",
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
