import argparse
from os import listdir
from util import load_circuit_structure
from old_codebase import synthesize

if __name__ == '__main__':
	"""
	>>> python separate_synth.py \
			block_files/qft_5_mesh_3_3_blocksize_3 \
			2
			shortest_path

	Synthesizes block_2 of already partitioned 
	`qft_5_mesh_3_3_blocksize_3_shortest-path` project.
	"""
	parser = argparse.ArgumentParser(
		description="Run synthesis on blocks in the `block_files` directory"
	)
	parser.add_argument("partition_dir", type=str, 
		help="path to block files to synthesize")
	parser.add_argument("edge_scheme", type=str,
		help="<shortest_path | nearest_physical | mst_path | mst_density>")
	parser.add_argument("block_number", type = int,
		help="specific block to synthesize")
	args = parser.parse_args()

	files = sorted(list(listdir(args.partition_dir)))
	files.remove("structure.pickle")

	target_name = args.partition_dir.split("/")[-1]
	target_name += "_kernel"
	block_name = files[args.block_number].split(".qasm")[0]

	qudit_group = load_circuit_structure(args.partition_dir)[args.block_number]
	options = {
		"target_name" : target_name,
		"synthesis_dir" : f"synthesis_files/{target_name}",
		"partition_dir" : f"{args.partition_dir}",
		"num_synth_procs" : 1,
		"checkpoint_as_qasm" : True,
	}

	synthesize(
		block_name,
		qudit_group,
		options,
	)