
benchmarks=(
	#"mult_16_preoptimized_mesh_16_blocksize_4_scan"
	#"hubbard_18_preoptimized_mesh_25_blocksize_4_scan"
	#"shor_26_preoptimized_mesh_36_blocksize_4_scan"
	#"tfim_40_preoptimized_mesh_49_blocksize_4_scan"
	#"qft_64_preoptimized_mesh_64_blocksize_4_scan"
	#"add_65_preoptimized_mesh_81_blocksize_4_scan"
	#"qft_100_preoptimized_mesh_100_blocksize_4_scan"
	#"add_101_preoptimized_mesh_121_blocksize_4_scan"
	#"mult_32_preoptimized_mesh_36_blocksize_4_scan"
	#"qft_10_preoptimized_mesh_16_blocksize_4_scan"
	#"qft_15_preoptimized_mesh_16_blocksize_4_scan"
	#"qft_25_preoptimized_mesh_25_blocksize_4_scan"
	#"qft_40_preoptimized_mesh_49_blocksize_4_scan"
	"qft_80_preoptimized_mesh_81_blocksize_4_scan"
)

types=(
	"lines"
	"stars"
	"rings"
	#"embedded"
)

python neighbors.py 

for benchmark in ${benchmarks[@]}
do
	for kernel in ${types[@]}
	do
		echo "${kernel}-${benchmark}"
		python neighbors.py "partitioned_circuits/${kernel}-${benchmark}.pickle" "subtopology_files/${kernel}-${benchmark}_kernel" "${kernel}"
	done
done
