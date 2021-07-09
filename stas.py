from __future__ import annotations
from sys import path
from typing import Any

from bqskit.ir.circuit import Circuit

from bqskit.compiler.passes.synthesis.leap import LEAPSynthesisPass
from bqskit.compiler.passes.synthesis.qfast import QFASTDecompositionPass
from bqskit.compiler.search.generators.simple import SimpleLayerGenerator
from bqskit.ir.gates.parameterized.unitary import VariableUnitaryGate

from bqskit.ir.lang.qasm2.qasm2 import OPENQASM2Language
from bqskit.compiler.machine import MachineModel
from bqskit.compiler.passes.partitioning.scan import ScanPartitioner
from bqskit.compiler.passes.util.unfold import UnfoldPass
from bqskit.compiler.passes.util.converttou3 import VariableToU3Pass
from bqskit.compiler.passes.util.converttou3 import PauliToU3Pass
from bqskit.compiler.passes.util.intermediate import SaveIntermediatePass

# Enable logging
import logging
logging.getLogger('bqskit').setLevel(logging.DEBUG)

from mapping import do_layout, do_routing, find_num_qudits
from mapping import dummy_layout, dummy_routing, find_num_qudits
from weighted_topology import get_hybrid_topology, get_logical_operations
from util import load_block_circuit, load_block_topology, load_circuit_structure, save_block_topology

from math import ceil, sqrt
from os.path import exists
from os import mkdir, listdir
import argparse
import pickle


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="Run subtopoloy aware synthesis"+\
		" based on the hybrid logical-physical topology scheme")
	parser.add_argument("qasm_files", nargs='+', type=str, 
		help="files to synthesize")
	parser.add_argument("--blocksize", dest="block_size", action="store",
		nargs='?', default=3, type=int, help="synthesis block size")
	parser.add_argument("--nearest_physical", action="store_true",
		help="add logical edges using nearest_physical scheme")
	parser.add_argument("--nearest_logical", action="store_true",
		help="add logical edges using nearest_logical scheme")
	parser.add_argument("--shortest_direct", action="store_true",
		help="add logical edges using shortest_direct scheme")
	args = parser.parse_args()

	for qasm_file in args.qasm_files:
		# Run setup
		#region setup
		num_q = find_num_qudits(qasm_file)
		num_p_sqrt = ceil(sqrt(num_q))
		coupling_map = "coupling_maps/mesh_%d_%d" %(num_p_sqrt, num_p_sqrt)
		checkpoint_as_qasm = True

		options = {
			"block_size"	 : args.block_size,
			"shortest_direct"  : args.shortest_direct,
			"nearest_logical"  : args.nearest_logical,
			"nearest_physical"  : args.nearest_physical,
			"is_qasm" : checkpoint_as_qasm,
			"estimated_cnots" : 0,
		}
		instantiate_options = {
			'min_iters': 0,
			'diff_tol_r': 1e-5,
			'dist_tol': 1e-11,
			'max_iters': 2500,
		}
		layer_generator = SimpleLayerGenerator(
			single_qudit_gate_1=VariableUnitaryGate(1),
		)

		edge_opts = [args.nearest_logical, args.nearest_physical, 
			args.shortest_direct]
		if not any(edge_opts):
			args.shortest_direct = True
		edge_opts = [args.nearest_logical, args.nearest_physical, 
			args.shortest_direct]
		if sum(edge_opts) != 1:
			raise ValueError(
				"Must have have a single logical edge scheme."
			)

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
		layout_qasm_file = "layout_qasm/" + target_name
		synthesized_qasm_file = "synthesized_qasm/" + target_name
		mapped_qasm_file = "mapped_qasm/" + target_name
		checkpoint_dir = "synthesis_files/" + target_name
		partition_dir = "block_files/" + target_name
		subtopology_dir = "subtopology_files/" + target_name

		#if not exists(checkpoint_dir):
		#	mkdir(checkpoint_dir)
		
		#endregion

		# Layout
		#region layout
		print("="*80)
		print("Doing layout for %s..." %(qasm_file))
		print("="*80)
		if exists(layout_qasm_file):
			print("Found existing file for %s, skipping layout" 
				%(layout_qasm_file))
		else:
			do_layout(qasm_file, coupling_map, layout_qasm_file)
			#dummy_layout(qasm_file, coupling_map, layout_qasm_file)
		#endregion

		# Partitioning on logical topology
		#region partitioning
		print("="*80)
		print("Doing logical partitioning on %s..." %(layout_qasm_file))
		print("="*80)
		# TODO: Errors if directory exists but does not have correct files
		if exists("block_files" + target_name):
			print(f"Found existing directory for block_files/{target_name}, "
				"skipping partitioning...")
		else:
			with open(layout_qasm_file, 'r') as f:
				circuit = OPENQASM2Language().decode(f.read())
			original = circuit.copy()
			logical_machine = MachineModel(num_p_sqrt**2, 
				get_logical_operations(circuit))
			partitioner = ScanPartitioner(args.block_size)
			partitioner.run(circuit, {"machine_model": logical_machine})
			saver = SaveIntermediatePass("block_files/", target_name,
				checkpoint_as_qasm)
			saver.run(circuit, {})
		block_files = sorted(listdir(partition_dir))
		if circuit is not None:
			# All blocks + the structure.pickle file
			if len(block_files) - 1 != circuit.get_num_operations():
				print(f"ERROR: Number of saved blocks in block_files/{target_name} "
					"do not match the number of partitions in circuit")
		block_names = []
		for bf in block_files:
			if not "structure.pickle" in bf:
				if checkpoint_as_qasm:
					block_names.append(bf.split(".qasm")[0])
				else:
					block_names.append(bf.split(".pickle")[0])
			else:
				block_files.remove(bf)
		#endregion

		# Subtopology analysis
		#region subtopology
		print("="*80)
		print(f"Doing subtopology analysis on {target_name}...")
		print("="*80)
		if not exists(subtopology_dir):
			mkdir(subtopology_dir)
		with open(f"{partition_dir}/structure.pickle", "rb") as f:
			structure = pickle.load(f)
		for block_num in range(len(block_files)):
			print(f"  Analyzing {block_names[block_num]}...")
			block_path = f"{partition_dir}/{block_files[block_num]}"
			subtopology = get_hybrid_topology(
				block_path, 
				coupling_map, 
				structure[block_num],
				options
			)
			subtopology_path = (
				f"{subtopology_dir}/{block_names[block_num]}"
				f"_subtopology.pickle"
			)
			save_block_topology(subtopology, subtopology_path)
		print(f"Estimated CNOT count: {options['estimated_cnots']}")
		#endregion

		# Synthesis
		#region synthesis
		print("="*80)
		print("Doing Synthesis on %s..." %(layout_qasm_file))
		print("="*80)
		if exists(synthesized_qasm_file):
			print("Found existing file for %s, skipping synthesis" 
				%(synthesized_qasm_file))
			print("="*80)
		else:
			synthesized_circuit = Circuit(num_p_sqrt**2)
			#synthesizer = LEAPSynthesisPass(
			#	layer_generator=layer_generator,
			#	instantiate_options=instantiate_options,
			#	#checkpoint_dir=checkpoint_dir
			#)
			structure = load_circuit_structure(partition_dir)
			for block_num in range(len(block_files)):
				# Load subtopology
				subtopology_path = (
					f"{subtopology_dir}/{block_names[block_num]}"
					f"_subtopology.pickle"
				)
				weighted_topology = load_block_topology(subtopology_path)
				subtopology = weighted_topology.subgraph(structure[block_num])
				# Get rid of weights for now
				# TODO: Add weighted edges to synthesis
				sub_edges = [(e[0], e[1]) for e in subtopology.edges]
				# Load circuit
				block_path = f"{partition_dir}/{block_files[block_num]}"
				subcircuit = load_block_circuit(block_path, options)
				unitary = subcircuit.get_unitary().get_numpy()
				subcircuit_qasm = OPENQASM2Language().encode(subcircuit)
				# Setup machine model
				print(f"  Synthesizing block {block_num}/{len(block_files)-1}")
				# Synthesize
				subcircuit_qasm = call_old_codebase_leap(
					unitary,
					list()
				)
				# Add to circuit
				synthesized_circuit.append_circuit(subcircuit, 
					structure[block_num])
			# Clean up synthesized qasm
			UnfoldPass().run(synthesized_circuit, {})
			VariableToU3Pass().run(synthesized_circuit, {})
			PauliToU3Pass().run(synthesized_circuit, {})
			with open(synthesized_qasm_file, 'w') as f:
				f.write(OPENQASM2Language().encode(synthesized_circuit))
			#endregion

			# Routing
			#region routing
			print("="*80)
			print("Doing Routing for %s..." %(synthesized_qasm_file))
			print("="*80)
			if exists(mapped_qasm_file):
				print("Found existing file for %s, skipping routing" 
					%(mapped_qasm_file))
			else:
				do_routing(synthesized_qasm_file, coupling_map, mapped_qasm_file)
				#dummy_routing(synthesized_qasm_file, coupling_map, mapped_qasm_file)
			#endregion
