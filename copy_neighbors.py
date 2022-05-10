import argparse
import os
import pickle

def check_subtopology_equal(edges_a, edges_b):
	for edge in edges_a:
		if edge not in edges_b:
			return False
	for edge in edges_b:
		if edge not in edges_a:
			return False
	return True

# Given a neighbors directory, check to see if we can copy over some
# already synthesized sythesis_files
if __name__ == '__main__':
	# inputs:
	# 	neighbors subtopology directory
	# 	neighbors synthesis_files directory
	# If neighbor and non-neighbor subtopology files are the same, copy over
	# the non-neighbor synthesis_file
	parser = argparse.ArgumentParser()
	parser.add_argument("neighbor_subtop_dir", type=str)
	parser.add_argument("neighbor_synth_dir", type=str)
	args = parser.parse_args()

	subtop = args.neighbor_subtop_dir.split("neighbors_")[-1]
	synth  = args.neighbor_synth_dir.split("neighbors_")[-1]
	non_subtop_dir = f"subtopology_files/{subtop}"
	non_synth_dir  = f"synthesis_files/{synth}"
	subtop_dir     = f"subtopology_files/neighbors_{subtop}"
	synth_dir      = f"synthesis_files/neighbors_{synth}"

	subtop_files = [x for x in sorted(os.listdir(subtop_dir)) if x.endswith('.pickle')]
	synth_files = [x for x in sorted(os.listdir(non_synth_dir)) if x.endswith('.qasm')]

	if len(subtop_files) != len(synth_files):
		raise RuntimeError(
			f"Unequal number of subtopology ({len(subtop_files)})"
			f"and synthesis files ({len(synth_files)}) on benchmark"
			f" {synth_dir}"
		)

	for block_num, subtop_file in enumerate(subtop_files):
		with open(non_subtop_dir + '/' + subtop_file, 'rb') as f:
			non_neighbor_topology = pickle.load(f)
		with open(subtop_dir + '/' + subtop_file, 'rb') as f:
			neighbor_topology = pickle.load(f)
		
		if check_subtopology_equal(non_neighbor_topology, neighbor_topology):
			# Copy non_neighbor synthesis file to neighbor synthesis dir
			with open(non_synth_dir + '/' + synth_files[block_num], 'r') as input_file:
				with open(synth_dir + '/' + synth_files[block_num], 'w') as output_file:
					output_file.write(input_file.read())
