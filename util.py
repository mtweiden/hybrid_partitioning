from __future__ import annotations
from typing import Any, Sequence
import pickle
import argparse

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
	coupling_map = "coupling_maps/mesh_%d_%d" %(num_p_sqrt, num_p_sqrt)
	checkpoint_as_qasm = True

	options = {
		"block_size"	 : args.block_size,
		"coupling_map"   : coupling_map,
		"shortest_direct"  : args.shortest_direct,
		"nearest_logical"  : args.nearest_logical,
		"nearest_physical"  : args.nearest_physical,
		"num_synth_procs" : args.num_synth_procs,
		"num_part_procs" : args.num_part_procs,
		"checkpoint_as_qasm" : checkpoint_as_qasm,
		"num_p" : num_p_sqrt ** 2,
		"physical_ops" : 0,
		"partitionable_ops" : 0,
		"unpartitionable_ops" : 0,
		"max_block_length" : 0,
		"min_block_length" : 0,
		"estimated_cnots" : 0,
        "physical_cost" : 0,
        "partitionable_cost" : 0,
        "unpartitionable_cost" : 0,
		"partitioner" : "scan"
	}

	edge_opts = [args.nearest_logical, args.nearest_physical, 
		args.shortest_direct]
	if not any(edge_opts):
		args.shortest_direct = True

	target_name = qasm_file.split("qasm/")[-1].split(".qasm")[0]
	target_name += "_" + coupling_map.split("coupling_maps/")[-1]
	target_name += f"_blocksize_{args.block_size}"

	options["layout_qasm_file"] = "layout_qasm/" + target_name
	options["partition_dir"] = "block_files/" + target_name
	options["save_part_name"] = target_name

	suffix = ""
	if args.shortest_direct:
		suffix += "_shortestdirect"
	elif args.nearest_physical:
		suffix += "_nearestphysical"
	elif args.nearest_logical:
		suffix += "_nearestlogical"

	target_name += suffix
	options["target_name"] = target_name
	options["synthesized_qasm_file"] = "synthesized_qasm/" + target_name
	options["mapped_qasm_file"] = "mapped_qasm/" + target_name
	options["synthesis_dir"] = "synthesis_files/" + target_name
	options["subtopology_dir"] = "subtopology_files/" + target_name

	return options

def print_summary(
	options : dict[str, Any], 
	total_ops : int, 
	block_files : Sequence[str]
) -> None:
	print(
		"Summary:\n"
		f"Number of blocks: {len(block_files)}\n"
		f"Mean block size (cnots): {total_ops/len(block_files)}\n"
		f"Total physical operations: {options['physical_ops']}\n"
		f"Total physical cost: {options['physical_cost']}\n"
		f"Total partitionable operations: {options['partitionable_ops']}\n"
		f"Total partitionable cost: {options['partitionable_cost']}\n"
		f"Total unpartitionable operations: {options['unpartitionable_ops']}\n"
		f"Total unpartitionable cost: {options['unpartitionable_cost']}\n"
		f"Estimated CNOT count: {options['estimated_cnots']}\n"
	)