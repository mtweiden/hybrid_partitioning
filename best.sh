
#python assemble_best.py synthesis_files/mult_16_preoptimized_mesh_16_blocksize_4_scan_kernel
#python assemble_best.py synthesis_files/hubbard_18_preoptimized_mesh_25_blocksize_4_scan_kernel
#python assemble_best.py synthesis_files/tfim_40_preoptimized_mesh_49_blocksize_4_scan_kernel
#python assemble_best.py synthesis_files/qft_64_preoptimized_mesh_64_blocksize_4_scan_kernel
#python assemble_best.py synthesis_files/add_65_preoptimized_mesh_81_blocksize_4_scan
#python assemble_best.py synthesis_files/shor_26_preoptimized_mesh_36_blocksize_4_scan_kernel

#rm synthesized_qasm/add_65*
python qutop.py --blocksize 4 --topology mesh --router qiskit --partitioner scan qasm/add_65_preoptimized.qasm --no_opt
#rm mapped_qasm/best-*qiskit*
#python qutop.py --blocksize 4 --topology mesh --router qiskit --partitioner scan qasm/best-mult_16_preoptimized.qasm
#python qutop.py --blocksize 4 --topology mesh --router qiskit --partitioner scan qasm/best-hubbard_18_preoptimized.qasm
#python qutop.py --blocksize 4 --topology mesh --router qiskit --partitioner scan qasm/best-tfim_40_preoptimized.qasm
#python qutop.py --blocksize 4 --topology mesh --router qiskit --partitioner scan qasm/best-qft_64_preoptimized.qasm
#python qutop.py --blocksize 4 --topology mesh --router qiskit --partitioner scan qasm/best-add_65_preoptimized.qasm
#python qutop.py --blocksize 4 --topology mesh --router pytket --partitioner scan qasm/best-shor_26_preoptimized.qasm
#python qutop.py --blocksize 4 --topology mesh --router qiskit --partitioner scan qasm/best-add_65_preoptimized.qasm
