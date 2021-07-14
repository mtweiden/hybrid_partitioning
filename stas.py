from __future__ import annotations
from typing import Any
from math import ceil, sqrt
from os.path import exists
from os import mkdir, listdir
import argparse
import pickle
from multiprocessing import Process

from bqskit.ir.circuit import Circuit
from bqskit.ir.lang.qasm2.qasm2 import OPENQASM2Language
from bqskit.compiler.machine import MachineModel
from bqskit.compiler.passes.partitioning.scan import ScanPartitioner
from bqskit.compiler.passes.util.intermediate import SaveIntermediatePass

from mapping import do_layout, do_routing, find_num_qudits
from mapping import dummy_layout, dummy_routing, find_num_qudits
from weighted_topology import get_hybrid_topology, get_logical_operations
from util import (
	load_block_circuit, 
	load_block_topology, 
	load_circuit_structure, 
	save_block_topology
)
from old_codebase import (
	call_old_codebase_leap, 
	check_for_leap_files, 
	parse_leap_files
)

# Enable logging
import logging
logging.getLogger('bqskit').setLevel(logging.DEBUG)


def synthesize(
	block_number : int,
	number_of_blocks : int,
	qudit_group : list[int],
	subtopology_path : str,
	block_path : str,
	options : dict[str, Any],
) -> None:
	# Get subcircuit QASM by loading checkpoint or by synthesis
	if check_for_leap_files(f"{options['target_name']}_block_{block_number}"):
		print(f"  Loading block {block_number+1}/{number_of_blocks}")
		subcircuit_qasm = parse_leap_files(
			f"{options['target_name']}_block_{block_number}"
		)
	else:
		# Load subtopology
		weighted_topology = load_block_topology(subtopology_path)
		subtopology = weighted_topology.subgraph(qudit_group)
		# Get rid of weights for now
		# TODO: Add weighted edges to synthesis function
		q_map = {qudit_group[k]:k for k in range(len(qudit_group))}
		sub_edges = [
			(q_map[e[0]], q_map[e[1]], subtopology[e[0]][e[1]]["weight"]) 
			for e in subtopology.edges
		]
		# Load circuit
		subcircuit = load_block_circuit(block_path, options)
		unitary = subcircuit.get_unitary().get_numpy()
		print(f"  Synthesizing block {block_number+1}/{number_of_blocks}")
		# Synthesize
		print("Using edges: ", sub_edges)
		subcircuit_qasm = call_old_codebase_leap(
			unitary,
			sub_edges,
			options["target_name"] + f"_block_{block_number}",
			options["num_synth_procs"],
		)
		with open(
			f"{options['checkpoint_dir']}_block_{block_number}.qasm", "w"
		) as f:
			f.write(subcircuit_qasm)
	

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
	}

	edge_opts = [args.nearest_logical, args.nearest_physical, 
		args.shortest_direct]
	if not any(edge_opts):
		args.shortest_direct = True

	target_name = qasm_file.split("qasm/")[-1].split(".qasm")[0]
	target_name += "_" + coupling_map.split("coupling_maps/")[-1]
	suffix = f"_blocksize_{args.block_size}"
	if args.shortest_direct:
		suffix += "_shortestdirect"
	elif args.nearest_physical:
		suffix += "_nearestphysical"
	elif args.nearest_logical:
		suffix += "_nearestlogical"
	target_name += suffix
	options["target_name"] = target_name
	options["layout_qasm_file"] = "layout_qasm/" + target_name
	options["synthesized_qasm_file"] = "synthesized_qasm/" + target_name
	options["mapped_qasm_file"] = "mapped_qasm/" + target_name
	options["checkpoint_dir"] = "synthesis_files/" + target_name
	options["partition_dir"] = "block_files/" + target_name
	options["subtopology_dir"] = "subtopology_files/" + target_name

	return options


if __name__ == '__main__':
	# Run setup
	#region setup
	parser = argparse.ArgumentParser(
		description="Run subtopoloy aware synthesis"
		" based on the hybrid logical-physical topology scheme"
	)
	parser.add_argument("qasm_file", type=str, help="file to synthesize")
	parser.add_argument("--blocksize", dest="block_size", action="store",
		nargs='?', default=3, type=int, help="synthesis block size")
	parser.add_argument("--nearest_physical", action="store_true",
		help="add logical edges using nearest_physical scheme")
	parser.add_argument("--nearest_logical", action="store_true",
		help="add logical edges using nearest_logical scheme")
	parser.add_argument("--shortest_direct", action="store_true",
		help="add logical edges using shortest_direct scheme")
	parser.add_argument("--num_synth_procs", dest="num_synth_procs", 
		action="store", nargs="?", default=1, type=int, 
		help="number of blocks to synthesize at once")
	parser.add_argument("--num_part_procs", dest="num_part_procs", 
		action="store", nargs="?", default=1, type=int, 
		help="number of processes while doing partitioning")
	parser.add_argument("--dummy_map", action="store_true",
		help="turn off layout and routing")
	args = parser.parse_args()
	#endregion

	options = setup_options(args.qasm_file, args)

	# Layout
	#region layout
	print("="*80, f"\nDoing layout for {args.qasm_file}...\n", "="*80) 
	if exists(options["layout_qasm_file"]):
		print("Found existing file for %s, skipping layout" 
			%(options["layout_qasm_file"]))
	else:
		if not args.dummy_map:
			do_layout(
				args.qasm_file, 
				options["coupling_map"], 
				options["layout_qasm_file"]
			)
		else:
			dummy_layout(
				args.qasm_file, 
				options["coupling_map"], 
				options["layout_qasm_file"]
			)
	#endregion

	# Partitioning on logical topology
	#region partitioning
	print("="*80)
	print("Doing logical partitioning on %s..." %(options["target_name"]))
	print("="*80)
	# TODO: Errors if directory exists but does not have correct files
	if exists(f"block_files/{options['target_name']}/finished"):
		print(
			"Found existing directory for block_files/"
			f"{options['target_name']}, skipping partitioning..."
		)
	else:
		with open(options["layout_qasm_file"], 'r') as f:
			circuit = OPENQASM2Language().decode(f.read())
		logical_machine = MachineModel(
			options["num_p"], 
			get_logical_operations(circuit)
		)
		partitioner = ScanPartitioner(args.block_size)
		partitioner.run(circuit, {"machine_model": logical_machine})
		saver = SaveIntermediatePass(
			"block_files/", 
			options["target_name"],
			options["checkpoint_as_qasm"]
		)
		saver.run(circuit, {})
		with open(
			f"block_files/{options['target_name']}/finished", "w"
		) as f:
			f.write("finished partitioning")
	block_files = sorted(listdir(options["partition_dir"]))
	block_names = []
	block_files.remove("structure.pickle")
	block_files.remove("finished")
	for bf in block_files:
		if options["checkpoint_as_qasm"]:
			block_names.append(bf.split(".qasm")[0])
		else:
			block_names.append(bf.split(".pickle")[0])
	#endregion

	# Subtopology analysis
	#region subtopology
	print("="*80)
	print(f"Doing subtopology analysis on {options['target_name']}...")
	print("="*80)
	if not exists(options["subtopology_dir"]):
		mkdir(options["subtopology_dir"])
	with open(f"{options['partition_dir']}/structure.pickle", "rb") as f:
		structure = pickle.load(f)
	for block_num in range(len(block_files)):
		print(f"  Analyzing {block_names[block_num]}...")
		block_path = f"{options['partition_dir']}/{block_files[block_num]}"
		subtopology = get_hybrid_topology(
			block_path, 
			options["coupling_map"], 
			structure[block_num],
			options
		)
		subtopology_path = (
			f"{options['subtopology_dir']}/{block_names[block_num]}"
			f"_subtopology.pickle"
		)
		save_block_topology(subtopology, subtopology_path)
	total_ops = sum([options["physical_ops"], options["partitionable_ops"],
		options["unpartitionable_ops"]])
	print("Summary:")
	print(f"Number of blocks: {len(block_files)}")
	print(f"Mean block size (cnots): {total_ops/len(block_files)}")
	print(f"Total physical operations: {options['physical_ops']}")
	print(f"Total partitionable operations: {options['partitionable_ops']}")
	print(f"Total unpartitionable operations: {options['unpartitionable_ops']}")
	print(f"Estimated CNOT count: {options['estimated_cnots']}")
	#endregion

	# Synthesis
	#region synthesis
	print("="*80)
	print(f"Doing Synthesis on {options['layout_qasm_file']}...")
	print("="*80)
	if exists(options['synthesized_qasm_file']):
		print(
			f"Found existing file for {options['synthesized_qasm_file']}, "
			"skipping synthesis\n",
			"="*80
		)
	else:
		synthesized_circuit = Circuit(options["num_p"])
		structure = load_circuit_structure(options["partition_dir"])
		block_list = list(range(0, len(block_files), 
			options["num_synth_procs"]))

		for block_num in block_list:
			processes = []
			for block_offset in range(options["num_synth_procs"]):
				# Do set ups
				block_number = block_num + block_offset
				print(
					f"    Synthesizing block {block_number+1}"
					f"/{len(block_files)}"
				)
				if block_number >= len(block_files):
					break
				subtopology_path = (
					f"{options['subtopology_dir']}/"
					f"{block_names[block_number]}_subtopology.pickle"
				)
				block_path = (
					f"{options['partition_dir']}/"
					f"{block_files[block_number]}"
				)
				# If uniprocessing, just call synthesis function
				if options["num_synth_procs"] == 1:
					synthesize(
						block_number=block_number,
						number_of_blocks=len(block_files),
						qudit_group=structure[block_number],
						subtopology_path=subtopology_path,
						block_path=block_path,
						options=options,
					)
				# If multiprocessing, launch new processes
				else:
					proc = Process(
						target=synthesize,
						args=(
							block_number,
							len(block_files),
							structure[block_number],
							subtopology_path,
							block_path,
							options
						)
					)
					processes.append(proc)
					proc.start()
			for proc in processes:
				proc.join()
					

		# Format QASM as subcircuit & add to circuit
		for block_num in range(len(block_files)):
			with open(
				f"{options['checkpoint_dir']}_block_{block_num}.qasm", "r"
			) as f:
				subcircuit_qasm = f.read()
			subcircuit = OPENQASM2Language().decode(subcircuit_qasm)
			qudit_group = structure[block_num]
			synthesized_circuit.append_circuit(subcircuit, qudit_group)

		with open(options["synthesized_qasm_file"], 'w') as f:
			f.write(OPENQASM2Language().encode(synthesized_circuit))
		#endregion

		# Routing
		#region routing
		print("="*80)
		print(f"Doing Routing for {options['synthesized_qasm_file']}...")
		print("="*80)
		if exists(options["mapped_qasm_file"]):
			print(
				f"Found existing file for {options['mapped_qasm_file']}, "
				"skipping routing" 
			)
		else:
			if not args.dummy_map:
				do_routing(
					options["synthesized_qasm_file"], 
					options["coupling_map"], 
					options["mapped_qasm_file"],
				)
			else:
				dummy_routing(
					options["synthesized_qasm_file"], 
					options["coupling_map"], 
					options["mapped_qasm_file"],
				)
		#endregion
	print("Summary:")
	print(f"Number of blocks: {len(block_files)}")
	print(f"Mean block size (cnots): {total_ops/len(block_files)}")
	print(f"Total physical operations: {options['physical_ops']}")
	print(f"Total partitionable operations: {options['partitionable_ops']}")
	print(f"Total unpartitionable operations: {options['unpartitionable_ops']}")
	print(f"Estimated CNOT count: {options['estimated_cnots']}")
