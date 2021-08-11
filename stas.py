from __future__ import annotations
from os.path import exists
from os import mkdir, listdir
import argparse
import pickle

from bqskit.ir.circuit import Circuit
from bqskit.ir.lang.qasm2.qasm2 import OPENQASM2Language
from bqskit.compiler.machine import MachineModel
from bqskit.compiler.passes.partitioning.scan import ScanPartitioner
from bqskit.compiler.passes.partitioning.greedy import GreedyPartitioner
from bqskit.compiler.passes.util.intermediate import SaveIntermediatePass

from mapping import do_layout, do_routing
from mapping import dummy_layout, dummy_routing, dummy_synthesis
from weighted_topology import get_best_qudit_group, get_hybrid_topology, get_logical_operations, run_stats
from util import (
	load_circuit_structure,
	rewrite_block,
	save_block_topology,
	save_circuit_structure,
	setup_options,
	get_summary,
)
from old_codebase import synthesize

# Enable logging
import logging
logging.getLogger('bqskit').setLevel(logging.INFO)



if __name__ == '__main__':
	# Run setup
	#region setup
	parser = argparse.ArgumentParser(
		description="Run subtopoloy aware synthesis"
		" based on the hybrid logical-physical topology scheme"
	)
	parser.add_argument("qasm_file", type=str, help="file to synthesize")
	parser.add_argument(
		"--blocksize", dest="blocksize", action="store", nargs='?', default=3,
		type=int, help="synthesis block size"
	)
	parser.add_argument(
		"--shortest_path", action="store_true",
		help="add logical edges using shortest_path scheme"
	)
	parser.add_argument(
		"--nearest_physical", action="store_true",
		help="add logical edges using nearest_physical scheme"
	)
	parser.add_argument(
		"--mst_path", action="store_true",
		help="add logical edges using mst_path scheme"
	)
	parser.add_argument(
		"--mst_density", action="store_true",
		help="add logical edges using mst_density scheme"
	)
	parser.add_argument(
		"--partitioner", dest="partitioner", action="store", nargs="?", 
		default="greedy", type=str, help="partitioner to use [scan | greedy]"
	)
	parser.add_argument(
		"--dummy_map", action="store_true", help="turn off layout and routing"
	)
	parser.add_argument(
		"--partition_only", action="store_true",
		help="skip synthesis and routing"
	)
	parser.add_argument("--coupling_map", dest="map_type", action="store",
		default="mesh", type=str,
		help="[mesh | linear]"
	)
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
	if exists(f"{options['partition_dir']}/structure.pickle"):
		print(
			f"Found existing files for {options['partition_dir']}"
			", skipping partitioning..."
		)
	else:
		with open(options["layout_qasm_file"], 'r') as f:
			circuit = OPENQASM2Language().decode(f.read())
		
		if options["partitioner"] == "greedy":
			partitioner = GreedyPartitioner(args.blocksize, "cost_based")
			#partitioner = GreedyPartitioner(args.blocksize)
		else:
			partitioner = ScanPartitioner(args.blocksize)

		machine_edges = get_logical_operations(circuit)
		logical_machine = MachineModel(
			options["num_p"], 
			machine_edges
		)
		data = {
			"machine_model": logical_machine,
		}

		partitioner.run(circuit, data)

		saver = SaveIntermediatePass(
			"block_files/", 
			options["save_part_name"],
			options["checkpoint_as_qasm"]
		)
		saver.run(circuit, {})

	block_files = sorted(listdir(options["partition_dir"]))
	block_names = []
	block_files.remove("structure.pickle")
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
	
	if exists(f"{options['subtopology_dir']}/summary.txt"):
		print(
			f"Found existing files for {options['subtopology_dir']},"
			" skipping subtopology generation..."
		)
	else:
		structure = load_circuit_structure(options["partition_dir"])
		for block_num in range(len(block_files)):
			print(f"  Analyzing {block_names[block_num]}...")
			block_path = f"{options['partition_dir']}/{block_files[block_num]}"

			# Check if qudits should be added to the block
			if len(structure[block_num]) < options["blocksize"]:
				old_group = structure[block_num]
				num_to_add = options['blocksize'] - len(old_group)
				new_group = get_best_qudit_group(
					block_path,
					structure[block_num],
					options,
				)
				print(f"  Added {len(new_group) - len(old_group)} qudits to {block_files[block_num]}")
				# Save new block qasm
				rewrite_block(block_path, old_group, new_group, options)
				# Save new qudit group structure
				structure[block_num] = new_group
				save_circuit_structure(options["partition_dir"], structure)

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
		summary = get_summary(options, block_files)
		with open(f"{options['subtopology_dir']}/summary.txt", "a") as f:
			f.write(summary)
	#endregion

	# Synthesis
	#region synthesis
	print("="*80)
	print(f"Doing Synthesis on {options['layout_qasm_file']}...")
	print("="*80)
	if exists(options['synthesized_qasm_file']):
		print(
			f"Found existing file for {options['synthesized_qasm_file']}, "
			"skipping synthesis\n", "="*80
		)
	elif not args.partition_only:
		synthesized_circuit = Circuit(options["num_p"])
		structure = load_circuit_structure(options["partition_dir"])
		block_list = list(range(0, len(block_files)))
		for block_number in block_list:
			# Blocks with very few qudits do not synthesize well, so don't
			if len(structure[block_number]) <= 2:
				print(
					f"    Block too small (size = {len(structure[block_number])})"
					f", skipping {block_files[block_number]}"
				)
				# copy the block file to the synthesis folder
				dummy_synthesis(
					block_name=block_names[block_number],
					options=options,
				)
			else:
				print(
					f"    Synthesizing block {block_number+1}/{len(block_files)}"
				)
				synthesize(
					block_name=block_names[block_number],
					qudit_group=structure[block_number],
					options=options,
				)

		# Format QASM as subcircuit & add to circuit
		for block_num in range(len(block_files)):
			with open(
				f"{options['synthesis_dir']}/{block_names[block_num]}.qasm",
				"r"
			) as f:
				subcircuit_qasm = f.read()
			subcircuit = OPENQASM2Language().decode(subcircuit_qasm)
			# Handle the case where the circuit is still smaller than the qudit
			# group, should only happen on circuits synthesized in an older
			# version.
			group_len = subcircuit.size
			qudit_group = [structure[block_num][x] for x in range(group_len)]
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
	#get_summary(options, block_files, True)
	print(run_stats(options, post_stats=False))
	if not args.partition_only:
		print(run_stats(options, post_stats=True))