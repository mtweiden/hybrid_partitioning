from __future__ import annotations
from sys import path
from typing import Any

from bqskit.ir.circuit import Circuit
from bqskit.ir.region import CircuitRegion
path.append("../bqskit")

from bqskit.compiler.passes.synthesis.leap import LEAPSynthesisPass
from bqskit.compiler.search.generators.simple import SimpleLayerGenerator
from bqskit.ir.gates.parameterized.unitary import VariableUnitaryGate

from bqskit.ir.lang.qasm2.qasm2 import OPENQASM2Language
from bqskit.compiler.machine import MachineModel
from bqskit.compiler.passes.partitioning.scan import ScanPartitioner
from bqskit.compiler.passes.util.unfold import UnfoldPass
from bqskit.compiler.passes.util.variabletou3 import VariableToU3Pass
from bqskit.compiler.passes.util.intermediate import SaveIntermediatePass

# Enable logging
import logging
logging.getLogger('bqskit').setLevel(logging.DEBUG)

from mapping import do_layout, do_routing, find_num_qudits
from mapping import dummy_layout, dummy_routing, find_num_qudits
from weighted_topology import get_hybrid_edge_set, load_hybrid_topology, save_hybrid_topology
from intermediate_results import check_for_synthesis_results, find_block_errors
from util import get_block

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
	parser.add_argument("--block_size", dest="block_size", action="store",
		nargs='?', default=3, type=int, help="synthesis block size")
	parser.add_argument("--reuse_edges", action="store_true",
		help="reuse logical edges in the hybrid topology")
	parser.add_argument("--shortest_path", action="store_true",
		help="use shortest paths in the physical topology to add logical edges")
	parser.add_argument("--add_interactors", action="store_true",
		help="add extra edges for strongly interacting qudits")
	args = parser.parse_args()

	for qasm_file in args.qasm_files:
		# Run setup
		#region setup
		num_q = find_num_qudits(qasm_file)
		num_p_sqrt = ceil(sqrt(num_q))
		coupling_map = "coupling_maps/mesh_%d_%d" %(num_p_sqrt, num_p_sqrt)
		checkpoint_as_qasm = False

		options = {
			"block_size"	 : args.block_size,
			"shortest_path"  : args.shortest_path,
			"is_qasm" : checkpoint_as_qasm
		}
		instantiate_options = {
			'min_iters': 0,
			'diff_tol_r': 1e-4,
			'dist_tol': 1e-11,
			'max_iters': 2500,
		}
		layer_generator = SimpleLayerGenerator(
			single_qudit_gate_1=VariableUnitaryGate(1),
		)

		target_name = qasm_file.split("qasm/")[-1].split(".qasm")[0]
		target_name += "_" + coupling_map.split("coupling_maps/")[-1]
		layout_qasm_file = "layout_qasm/" + target_name
		synthesized_qasm_file = "synthesized_qasm/" + target_name \
			+ "_blocksize_" + str(args.block_size)
		mapped_qasm_file = "mapped_qasm/" + target_name \
			+ "_blocksize_" + str(args.block_size)
		checkpoint_dir = "synthesis_files/" + target_name \
			+ "_blocksize_" + str(args.block_size)
		partition_dir = "block_files/" + target_name \
			+ "_blocksize_" + str(args.block_size)
		if args.reuse_edges:
			layout_qasm_file += "_reuseedges"
			synthesized_qasm_file += "_reuseedges"
			mapped_qasm_file += "_reuseedges"
			checkpoint_dir += "_reuseedges"
		if args.shortest_path:
			layout_qasm_file += "_shortestpath"
			synthesized_qasm_file += "_shortestpath"
			mapped_qasm_file += "_shortestpath"
			checkpoint_dir += "_shortestpath"
		if args.add_interactors:
			layout_qasm_file += "_addinteractors"
			synthesized_qasm_file += "_addinteractors"
			mapped_qasm_file += "_addinteractors"
			checkpoint_dir += "_addinteractors"

		if not exists(checkpoint_dir):
			mkdir(checkpoint_dir)
		
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
			og_circ = circuit.copy()
			ScanPartitioner(args.block_size).run(circuit, {})
			proj_name = target_name + "_blocksize_" + str(args.block_size)
			SaveIntermediatePass(
				"block_files/", 
				proj_name, 
				checkpoint_as_qasm
			).run(circuit, {})
		block_files = sorted(listdir(partition_dir))
		if circuit is not None:
			# All blocks + the structure.pickle file
			if len(block_files) - 1 != circuit.get_num_operations():
				print(f"ERROR: Number of saved blocks in block_files/{target_name} "
					"do not match the number of partitions in circuit")
		for bf in block_files:
			if "structure.pickle" in bf:
				block_files.remove(bf)
		#endregion

		# Subtopology analysis
		#region subtopology
		print("="*80)
		print(f"Doing subtopology analysis on {target_name}...")
		print("="*80)
		if not exists(f"subtopology_files/{target_name}"):
			mkdir(f"subtopology_files/{target_name}")
		for block_file in block_files:
			print(f"  Analyzing {block_file}...")
			block_path = f"{partition_dir}/{block_file}"
			subtopology = get_hybrid_edge_set(block_path, coupling_map, options)
			subtopology_path = f"{target_name}/{block_file}"
			save_hybrid_topology(subtopology, subtopology_path, coupling_map, options)
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
			synthesizer = LEAPSynthesisPass(
				layer_generator=layer_generator,
				instantiate_options=instantiate_options,
				#checkpoint_dir=checkpoint_dir
			)
			with open(f"{partition_dir}/structure.pickle", "rb") as f:
				structure = pickle.load(f)
			for block_num in range(len(block_files)):
				block_path = f"{partition_dir}/{block_files[block_num]}"
				subtopology_path = f"{target_name}/{block_files[block_num]}"
				subtopology = load_hybrid_topology(subtopology_path, coupling_map, options)
				subcircuit = get_block(block_path, options)
				region = CircuitRegion({q: (0, subcircuit.get_depth() - 1) 
					for q in range(subcircuit.get_size())})
				subcircuit.fold(region)
				machine = MachineModel(circuit.get_size(), subtopology)
				data = {"machine_model": machine}
				print(f"  Synthesizing block {block_num}/{len(block_files)-1}")
				synthesizer.run(subcircuit, data)
				synthesized_circuit.append_circuit(subcircuit, structure[block_num])
			# Clean up synthesized qasm
			UnfoldPass().run(synthesized_circuit, {})
			VariableToU3Pass().run(synthesized_circuit, {})
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
