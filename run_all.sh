#! /bin/bash
#"qft_50 qft_64 qft_100 add_17 add_41 add_65 add_101 hubbard_4 hubbard_18" 
#"shor_18 shor_26 shor_42 shor_62 ev"
files="qsp_20 qsp_40 qsp_60  qsp_80  qsp_100 qsp_120" 
#files="tfim_4 tfim_10 tfim_20 tfim_60 tfim_100 qft_50 qft_64 qft_100 add_17 add_41 add_65 add_101 hubbard_4 hubbard_18" 
routers="falcon"
for file_val in $files; do
	for router_val in $routers; do
		echo "python stas.py qasm/$file_val.qasm --blocksize 4 --partition_only --topology $router_val"
		python stas.py qasm/$file_val.qasm --blocksize 4 --partition_only --topology $router_val
		echo "python replace_blocks.py qasm/$file_val.qasm --blocksize 4 --partition_only --topology $router_val"
		python replace_blocks.py qasm/$file_val.qasm --blocksize 4 --partition_only --topology $router_val
	done
done
