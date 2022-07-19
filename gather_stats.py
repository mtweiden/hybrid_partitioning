import pickle
from os import listdir
import re
from statistics import median, mean, stdev
from bqskit import Circuit

benchmarks=[
	#"mult_16_preoptimized_mesh_16_blocksize_4_scan",
	#"mult_32_preoptimized_mesh_36_blocksize_4_scan",
	#"qft_64_preoptimized_mesh_64_blocksize_4_scan",
	#"qft_100_preoptimized_mesh_100_blocksize_4_scan",
	#"add_65_preoptimized_mesh_81_blocksize_4_scan",
	#"add_101_preoptimized_mesh_121_blocksize_4_scan",
	#"tfim_40_preoptimized_mesh_49_blocksize_4_scan",
	#"tfim_100_preoptimized_mesh_100_blocksize_4_scan",
	#"hubbard_18_preoptimized_mesh_25_blocksize_4_scan",
	#"shor_26_preoptimized_mesh_36_blocksize_4_scan"
	"mult_16_preoptimized_falcon_16_blocksize_4_scan",
	"mult_32_preoptimized_falcon_65_blocksize_4_scan",
	"qft_64_preoptimized_falcon_65_blocksize_4_scan",
	"qft_100_preoptimized_falcon_113_blocksize_4_scan",
	"add_65_preoptimized_falcon_65_blocksize_4_scan",
	"add_101_preoptimized_falcon_113_blocksize_4_scan",
	"tfim_40_preoptimized_falcon_65_blocksize_4_scan",
	"tfim_100_preoptimized_falcon_113_blocksize_4_scan",
	"hubbard_18_preoptimized_falcon_27_blocksize_4_scan",
	"shor_26_preoptimized_falcon_27_blocksize_4_scan"
]

if __name__ == '__main__':
	stat_list = []
	for benchmark in benchmarks:
		block_files = [
			x for x in sorted(listdir(f'block_files/{benchmark}'))
			if x.endswith('.qasm')
		]
		cnot_counts = []
		error_in_blocks = []
		for block in block_files:
			cnots_in_block = 0
			with open(f'block_files/{benchmark}/{block}', 'r') as f:
				for line in f.readlines():
					if re.match('cx', line):
						cnots_in_block += 1
			#original_circuit = Circuit(1).from_file(f'block_files/{benchmark}/{block}')
			#original_unitary = original_circuit.get_unitary()
			#synth_circuit = Circuit(1).from_file(f'synthesis_files/{benchmark}_kernel/{block}')
			#synth_unitary = synth_circuit.get_unitary()
			#error_in_blocks.append(synth_unitary.get_distance_from(original_unitary))
			cnot_counts.append(cnots_in_block)

		mean_cnots   = mean(cnot_counts)
		stdev_cnots  = stdev(cnot_counts)
		median_cnots = median(cnot_counts)

		stat_list.append(
			(
				benchmark,
				len(cnot_counts),
				#sum(error_in_blocks),
				mean_cnots,
				stdev_cnots,
				median_cnots
			)
		)
	print(stat_list)
