from __future__ import annotations
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

from mapping import do_layout, do_routing
from mapping import dummy_layout, dummy_routing
from weighted_topology import get_hybrid_topology, get_logical_operations
from util import (
	load_circuit_structure, 
	save_block_topology,
	setup_options,
	print_summary,
)
from old_codebase import synthesize

# Enable logging
import logging
logging.getLogger('bqskit').setLevel(logging.DEBUG)



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
	parser.add_argument("--partition_only", action="store_true",
		help="skip synthesis and routing")
	args = parser.parse_args()
	#endregion

	options = setup_options(args.qasm_file, args)
	if not exists(options["synthesis_dir"]):
		mkdir(options["synthesis_dir"])

	# Layout
	#region layout
	print("="*80)
	print(f"Doing layout for {options['target_name']}...")
	print("="*80) 
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
	if exists(f"{options['partition_dir']}/finished"):
		print(
			f"Found existing directory for {options['partition_dir']}"
			", skipping partitioning..."
		)
	else:
		with open(options["layout_qasm_file"], 'r') as f:
			circuit = OPENQASM2Language().decode(f.read())
		logical_machine = MachineModel(
			options["num_p"], 
			get_logical_operations(circuit)
		)
		partitioner = ScanPartitioner(args.block_size)
		data = {
			"machine_model": logical_machine,
			"keep_idle_qudits": True
		}
		partitioner.run(circuit, data)
		saver = SaveIntermediatePass(
			"block_files/", 
			options["save_part_name"],
			options["checkpoint_as_qasm"]
		)
		saver.run(circuit, {})
		with open(
			f"{options['partition_dir']}/finished", "w"
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
	print_summary(options, total_ops, block_files)
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
	elif not args.partition_only:
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
				# If uniprocessing, just call synthesis function
				if options["num_synth_procs"] == 1:
					synthesize(
						block_name=block_names[block_number],
						qudit_group=structure[block_number],
						options=options,
					)
				# If multiprocessing, launch new processes
				else:
					proc = Process(
						target=synthesize,
						args=(
							block_number,
							structure[block_number],
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
				f"{options['synthesis_dir']}/{block_names[block_num]}.qasm",
				"r"
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
		elif not args.partition_only:
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
	print_summary(options, total_ops, block_files)