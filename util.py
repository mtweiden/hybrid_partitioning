from __future__ import annotations
from posix import listdir
from re import S, match
from typing import Any, Sequence
import pickle
import argparse

from qiskit import circuit

from networkx.classes.graph import Graph
from math import sqrt, ceil
from bqskit import Circuit
from bqskit.ir.gates.circuitgate import CircuitGate
from bqskit.ir.lang.qasm2.qasm2	import OPENQASM2Language
from bqskit.ir.region import CircuitRegion

from mapping import find_num_qudits

def load_block_circuit(
	block_path : str,
	options : dict[str, Any]
) -> Circuit:
	if options['checkpoint_as_qasm']:
		with open(block_path, "r") as f:
			return OPENQASM2Language().decode(f.read())
	else:
		with open(block_path, 'rb') as f:
			return pickle.load(f)

def save_block_circuit(
	block_path : str,
	block_circuit : Circuit,
	options : dict[str, Any]
) -> None:
	if options['checkpoint_as_qasm']:
		qasm = OPENQASM2Language().encode(block_circuit)
		with open(block_path, "w") as f:
			f.write(qasm)
	else:
		with open(block_path, 'wb') as f:
			pickle.dump(block_circuit, f)


def load_block_topology(
	block_path : str,
) -> Graph:
	with open(block_path, "rb") as f:
		return pickle.load(f)


def save_block_topology(
	subtopology: Graph,
	block_path : str,
) -> None:
	with open(block_path, 'wb') as f:
		pickle.dump(subtopology, f)


def save_circuit_structure(
	partition_directory: str,
	structure_list : Sequence[Sequence[int]],
) -> None:
	with open(f"{partition_directory}/structure.pickle", "wb") as f:
		pickle.dump(structure_list, f)


def load_circuit_structure(
	partition_directory : str,
) -> Sequence[Sequence[int]]:
	with open(f"{partition_directory}/structure.pickle", "rb") as f:
		return pickle.load(f)


def careful_fold(
	circuit : Circuit,
) -> Circuit:
	"""
	Needed for maintaining CircuitGate sizes.

	Args:
		circuit (Circuit): Circuit to be folded.

	Returns:
		Circuit: The CircuitGate version of `circuit`.
	"""
	region = CircuitRegion({q: (0, circuit.get_depth() - 1) 
		for q in range(circuit.get_size())})
	folded_circuit = Circuit(circuit.get_size(), circuit.get_radixes())
	small_region = circuit.downsize_region(region)
	cgc = circuit.get_slice(small_region.points)
	if len(region.location) > len(small_region.location):
		for i in range(len(region.location)):
			if region.location[i] not in small_region.location:
				cgc.insert_qudit(i)
	folded_circuit.append_gate(
		CircuitGate(cgc, True),
		sorted(list(region.keys())),
		list(cgc.get_params()),
	)
	return folded_circuit


def setup_options(
	qasm_file : str, 
	args : argparse.Namespace
) -> dict[str,Any]:

	num_q = find_num_qudits(qasm_file)
	num_p_sqrt = ceil(sqrt(num_q))

	# Select coupling map
	valid_map_types = ["mesh", "linear"]
	if not args.map_type in valid_map_types:
		raise RuntimeError(
			f"{args.map_type} is not a valid coupling map type."
		)
	coupling_map = (
		f"coupling_maps/{args.map_type}_{num_p_sqrt}_{num_p_sqrt}"
	)

	# Select partitioner
	valid_partitioners = ["scan", "greedy", "custom"]
	if not args.partitioner in valid_partitioners:
		raise RuntimeError(
			f"{args.partitioner} is not a valid partitioner type."
		)
	partitioner = args.partitioner

	options = {
		"blocksize"	 : args.blocksize,
		"coupling_map"   : coupling_map,
		"shortest_path" : args.shortest_path,
		"nearest_physical"  : args.nearest_physical,
		"mst_path" : args.mst_path,
		"mst_density" : args.mst_density,
		"partitioner" : partitioner,
		"checkpoint_as_qasm" : True,
		"num_p" : num_p_sqrt ** 2,
		"direct_ops" : 0,
		"indirect_ops" : 0,
		"external_ops" : 0,
        "direct_volume" : 0,
        "indirect_volume" : 0,
        "external_volume" : 0,
		"max_block_length" : 0,
		"min_block_length" : 0,
		"estimated_cnots" : 0,
		"total_volume" : 0,
	}

	target_name = qasm_file.split("qasm/")[-1].split(".qasm")[0]
	target_name += "_" + coupling_map.split("coupling_maps/")[-1]
	target_name += f"_blocksize_{args.blocksize}"

	options["layout_qasm_file"] = "layout_qasm/" + target_name

	if partitioner != "scan":
		target_name += f"_{partitioner}"

	options["partition_dir"] = "block_files/" + target_name
	options["save_part_name"] = target_name

	edge_opts = [
		args.shortest_path, 
		args.nearest_physical, 
		args.mst_path, 
		args.mst_density, 
	]
	if not any(edge_opts):
		args.shortest_path = True

	suffix = ""
	if args.shortest_path:
		suffix += "_shortest-path"
	elif args.nearest_physical:
		suffix += "_nearest-physical"
	elif args.mst_path:
		suffix += "_mst-path" # Was nearest_logical
	elif args.mst_density:
		suffix += "_mst-density"

	target_name += suffix
	options["target_name"] = target_name
	options["synthesized_qasm_file"] = "synthesized_qasm/" + target_name
	options["mapped_qasm_file"] = "mapped_qasm/" + target_name
	options["synthesis_dir"] = "synthesis_files/" + target_name
	options["subtopology_dir"] = "subtopology_files/" + target_name

	return options

def get_summary(
	options : dict[str, Any], 
	block_files : Sequence[str],
	post_flag : bool = False,
) -> str:
	total_ops = sum([options["direct_ops"], options["indirect_ops"], 
		options["external_ops"]])
	string = (
		"\nSummary:\n"
		f"Number of blocks: {len(block_files)}\n"
		f"Mean block size (cnots): {total_ops/len(block_files)}\n\n"
		f"Total internal direct operations: {options['direct_ops']}\n"
		f"Total internal direct volume: {options['direct_volume']}\n"
		f"Total internal indirect operations: {options['indirect_ops']}\n"
		f"Total internal indirect volume: {options['indirect_volume']}\n"
		f"Total external operations: {options['external_ops']}\n"
		f"Total external volume: {options['external_volume']}\n"
	)
	if post_flag:
		string += get_mapping_results(options)
		string += get_original_count(options)
	print(string)
	return string

def get_mapping_results(
	options : dict[str, Any],
) -> str:
	path = options["mapped_qasm_file"]
	cnots = 0
	swaps = 0
	with open(path, "r") as qasmfile:
		for line in qasmfile:
			if match("cx", line):
				cnots += 1
			elif match("swap", line):
				swaps += 1
	return f"Synthesized CNOTs: {cnots}\nSWAPs from routing: {swaps}\n"

def get_original_count(
	options : dict[str, Any],
) -> str:
	path = options["layout_qasm_file"]
	cnots = 0
	with open(path, "r") as qasmfile:
		for line in qasmfile:
			if match("cx", line):
				cnots += 1
	return f"Original CNOTs: {cnots}\n"


def rewrite_block(
	block_path : str,
	original_qudit_group : Sequence[int],
	new_qudit_group : Sequence[int],
	options : dict[str, Any],
) -> None:
	circuit = load_block_circuit(block_path, options)

	for i, qudit in enumerate(sorted(new_qudit_group)):
		if qudit in original_qudit_group:
			continue
		circuit.insert_qudit(i)
	
	save_block_circuit(block_path, circuit, options)
