from __future__ import annotations
from os.path import exists
from os import mkdir, listdir
import argparse
import pickle
from partition_analysis import PartitionAnalyzer
from post_synth import replace_blocks

from bqskit.ir.circuit import Circuit
from bqskit.ir.lang.qasm2.qasm2 import OPENQASM2Language
from bqskit.compiler.machine import MachineModel
from bqskit.passes.partitioning.scan import ScanPartitioner
from bqskit.passes.partitioning.greedy import GreedyPartitioner
from bqskit.passes.partitioning.quick import QuickPartitioner
from bqskit.passes.util.intermediate import SaveIntermediatePass

from mapping import do_layout, do_routing, manual_layout, random_layout
from mapping import dummy_layout, dummy_routing, dummy_synthesis
from topology import get_logical_operations, kernel_type, run_stats, match_kernel
from util import (
	load_circuit_structure,
	save_block_topology,
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
	parser.add_argument(
		"qasm_file", type=str, help="file to compare",
		default="qasm/qft_10.qasm"
	)
	parser.add_argument(
		"--blocksize", dest="blocksize", action="store", nargs='?', default=4,
		type=int, help="synthesis block size"
	)
	parser.add_argument(
		"--partitioner", dest="partitioner", action="store", nargs="?", 
		default="quick", type=str, help="partitioner to use [scan | greedy]"
	)
	parser.add_argument(
		"--dummy_map", action="store_true",
		help="skip synthesis and routing"
	)
	parser.add_argument(
		"--partition_only", action="store_true",
		help="skip synthesis and routing"
	)
	parser.add_argument("--topology", dest="map_type", action="store",
		default="mesh", type=str,
		help="[mesh | linear | falcon]"
	)
	parser.add_argument("--router", dest="router", action="store",
		default="qiskit", type=str,
		help="[pytket | qiskit]"
	)
	parser.add_argument("--alltoall",action="store_true",
		help="synthesize to all to all"
	)
	parser.add_argument("--layout", dest="layout", action="store",
		default="none", type=str,
		help="[none | random | sabre]"
	)
	parser.add_argument("--synthesis_impact", action="store_true",
		help="Run comparison between non-synthesis and synthesis versions")
	args = parser.parse_args()
	#endregion

	options = setup_options(args.qasm_file, args)
	if not exists(options["synthesis_dir"]):
		mkdir(options["synthesis_dir"])

	## Layout
	##region layout
	#print("="*80)
	#print(f"Doing layout for unsynthesized {options['unsynthesized_layout']}...")
	#print("="*80) 
	if not exists(options["unsynthesized_layout"]):
		l2p_mapping = manual_layout(
			options["layout_qasm_file"],
			options["relayout_remapping_file"],
			options["unsynthesized_layout"],
			options
		)
		with open(options["unsynthesized_qubit_remapping"], "wb") as f:
			pickle.dump(l2p_mapping, f)
	#else:
	#	print(
	#		f"Found existing file for {options['unsynthesized_layout']}, "
	#		"skipping layout"
	#	)

	#endregion

	block_files = sorted(listdir(options["partition_dir"]))
	block_names = []
	block_files.remove("structure.pickle")
	for bf in block_files:
		if options["checkpoint_as_qasm"]:
			block_names.append(bf.split(".qasm")[0])
		else:
			block_names.append(bf.split(".pickle")[0])
	#endregion

	## Routing
	##region routing
	#print("="*80)
	#print(f"Doing Routing for {options['unsynthesized_layout']}...")
	#print("="*80)
	if not exists(options["unsynthesized_mapping"]):
		l2p_mapping = do_routing(
			options["unsynthesized_layout"], 
			options["coupling_map"], 
			options["unsynthesized_mapping"],
			options,
		)
	#else:
	#	print(
	#		f"Found existing file for {options['unsynthesized_mapping']}, "
	#		"skipping routing" 
	#	)
	#endregion

	## Collect stats
	##region collections
	#print("="*80)
	#print(f"Collecting stats about each partiiton")
	#print("="*80)
	if args.synthesis_impact:
		mapped_analysis = options["mapped_qasm_file"]
		block_dir = options["synthesis_dir"]
		remapping_file = options["relayout_remapping_file"]
	else:
		mapped_analysis = options["unsynthesized_mapping"]
		#mapped_analysis = options["unsynthesized_layout"]
		block_dir = options["partition_dir"]
		remapping_file = options["unsynthesized_qubit_remapping"]
		#remapping_file = options["relayout_remapping_file"]

	# Convert structure using mapping data
	with open(f"{options['partition_dir']}/structure.pickle", "rb") as f:
		structure = pickle.load(f)
	with open(remapping_file, "rb") as f:
		l2p_mapping = pickle.load(f)
	new_structure = []
	for qudit_group in structure:
		new_group = []
		for qudit in qudit_group:
			new_group.append(l2p_mapping[qudit])
		new_structure.append(new_group)

	# Get list of all block subtopologies
	subtopology_list = sorted(listdir(options['subtopology_dir']))
	subtopology_list.remove("summary.txt")

	analyzer = PartitionAnalyzer(
		mapped_analysis,
		block_dir,
		block_files,
		new_structure,
		options["num_p"],
		options["subtopology_dir"],
		subtopology_list,
	)

	analyzer.run()
	
	#endregion
