#	partition_dir		subtopology_dir
benchmarks=(
	"qft_64_preoptimized_mesh_64_blocksize_3_quick"
	"qft_100_preoptimized_mesh_100_blocksize_3_quick"
	"add_65_preoptimized_mesh_81_blocksize_3_quick"
	"add_101_preoptimized_mesh_121_blocksize_3_quick"
	"hubbard_18_preoptimized_mesh_25_blocksize_3_quick"
	"shor_26_preoptimized_mesh_36_blocksize_3_quick"
	"qsp_60_preoptimized_mesh_64_blocksize_3_quick"
	"qsp_80_preoptimized_mesh_81_blocksize_3_quick"
	"qsp_120_preoptimized_mesh_121_blocksize_3_quick"
	"tfim_60_preoptimized_mesh_64_blocksize_3_quick"
	"tfim_100_preoptimized_mesh_100_blocksize_3_quick"

	"qft_64_preoptimized_mesh_64_blocksize_4_quick"
	"qft_100_preoptimized_mesh_100_blocksize_4_quick"
	"add_65_preoptimized_mesh_81_blocksize_4_quick"
	"add_101_preoptimized_mesh_121_blocksize_4_quick"
	"hubbard_18_preoptimized_mesh_25_blocksize_4_quick"
	"shor_26_preoptimized_mesh_36_blocksize_4_quick"
	"qsp_60_preoptimized_mesh_64_blocksize_4_quick"
	"qsp_80_preoptimized_mesh_81_blocksize_4_quick"
	"qsp_120_preoptimized_mesh_121_blocksize_4_quick"
	"tfim_60_preoptimized_mesh_64_blocksize_4_quick"
	"tfim_100_preoptimized_mesh_100_blocksize_4_quick"

	"qft_64_preoptimized_mesh_64_blocksize_5_quick"
	"qft_100_preoptimized_mesh_100_blocksize_5_quick"
	"add_65_preoptimized_mesh_81_blocksize_5_quick"
	"add_101_preoptimized_mesh_121_blocksize_5_quick"
	"hubbard_18_preoptimized_mesh_25_blocksize_5_quick"
	"shor_26_preoptimized_mesh_36_blocksize_5_quick"
	"qsp_60_preoptimized_mesh_64_blocksize_5_quick"
	"qsp_80_preoptimized_mesh_81_blocksize_5_quick"
	"qsp_120_preoptimized_mesh_121_blocksize_5_quick"
	"tfim_60_preoptimized_mesh_64_blocksize_5_quick"
	"tfim_100_preoptimized_mesh_100_blocksize_5_quick"
)

for benchmark in ${benchmarks[@]}
do
	#echo $benchmark "${benchmark}_kernel"
	echo $benchmark
	python connectivity.py "block_files/${benchmark}" "subtopology_files/${benchmark}_kernel" "synthesis_files/${benchmark}_kernel"
done
