from __future__ import annotations
from sys import path
path.append("../bqskit")

from bqskit.compiler.passes.synthesis.leap import LEAPSynthesisPass
from bqskit.compiler.search.generators.simple import SimpleLayerGenerator
from bqskit.ir.gates.parameterized.unitary import VariableUnitaryGate

from bqskit.ir.lang.qasm2.qasm2 import OPENQASM2Language
from bqskit.compiler.machine import MachineModel
from bqskit.compiler.passes.partitioning.scan import ScanPartitioner
from bqskit.compiler.passes.util.unfold import UnfoldPass
from bqskit.compiler.passes.util.variabletou3 import VariableToU3Pass

# Enable logging
import logging
logging.getLogger('bqskit').setLevel(logging.DEBUG)

from mapping import do_layout, do_routing, find_num_qudits
from hybrid_topology import get_hybrid_edge_set, save_hybrid_topology
from intermediate_results import check_for_synthesis_results, find_block_errors

from math import ceil, sqrt
from os.path import exists
from os import mkdir
import argparse
import pickle


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="Run topoloy aware synthesis"+\
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
		num_q = find_num_qudits(qasm_file)
		num_p = ceil(sqrt(num_q))
		coupling_map = "coupling_maps/mesh_%d_%d" %(num_p, num_p)

		options = {
			"block_size"	 : args.block_size,
			"reuse_edges"	: args.reuse_edges,
			"shortest_path"  : args.shortest_path,
			"add_interactors": args.add_interactors
		}

		target_name = qasm_file.split("qasm/")[-1].split(".qasm")[0]
		target_name += "_" + coupling_map.split("coupling_maps/")[-1]
		layout_qasm_file = "layout_qasm/" + target_name
		synthesized_qasm_file = "synthesized_qasm/" + target_name \
			+ "_blocksize_" + str(args.block_size)
		mapped_qasm_file = "mapped_qasm/" + target_name \
			+ "_blocksize_" + str(args.block_size)
		checkpoint_dir = "leap_files/" + target_name \
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

		print("="*80)
		print("Doing Layout for %s..." %(qasm_file))
		print("="*80)
		#if exists(layout_qasm_file):
		#	print("Found existing file for %s, skipping layout" 
		#		%(layout_qasm_file))
		#else:
		#	do_layout(qasm_file, coupling_map, layout_qasm_file)
		do_layout(qasm_file, coupling_map, layout_qasm_file)

		# Routing
		print("="*80)
		print("Doing Routing for %s..." %(layout_qasm_file))
		print("="*80)
		#if exists(mapped_qasm_file):
		#	print("Found existing file for %s, skipping routing" 
		#		%(mapped_qasm_file))
		#else:
		#	do_routing(layout_qasm_file, coupling_map, mapped_qasm_file)
		do_routing(layout_qasm_file, coupling_map, mapped_qasm_file)

		## Physical Connectivity
		with open(coupling_map, 'rb') as f:
			physical_topology = pickle.load(f)

		## Partitioning and synthesis
		print("="*80)
		print("Doing Partitioning on %s..." %(mapped_qasm_file))
		print("="*80)
		#if exists(synthesized_qasm_file):
		#	print("Found existing file for %s, skipping synthesis" 
		#		%(synthesized_qasm_file))
		#else:
		if True:
			with open(mapped_qasm_file, 'r') as f:
				circuit = OPENQASM2Language().decode(f.read())
			partitioner = ScanPartitioner(args.block_size)
			machine = MachineModel(circuit.get_size(), physical_topology)
			data = {"machine_model": machine}
			partitioner.run(circuit, data)
			instantiate_options = {
				'min_iters': 0,
				'diff_tol_r': 1e-4,
				'dist_tol': 1e-11,
				'max_iters': 2500,
			}
			layer_generator = SimpleLayerGenerator(
				single_qudit_gate_1=VariableUnitaryGate(1),
			)
			synthesizer = LEAPSynthesisPass(
				layer_generator=layer_generator,
				instantiate_options=instantiate_options,
				checkpoint_dir=checkpoint_dir
			)
			print("="*80)
			print("Doing Synthesis on %s..." %(mapped_qasm_file))
			print("="*80)
			synthesizer.run(circuit, data)
			UnfoldPass().run(circuit, data)
			VariableToU3Pass().run(circuit, data)

			# Clean up synthesized qasm
			with open(synthesized_qasm_file, 'w') as f:
				f.write(OPENQASM2Language().encode(circuit))

