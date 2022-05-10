
python qutop.py --blocksize 4 --topology mesh --partition_only --partitioner scan qasm/best-mult_16_preoptimized.qasm

python qutop.py --blocksize 4 --topology mesh --partition_only --partitioner scan qasm/best-hubbard_18_preoptimized.qasm

python qutop.py --blocksize 4 --topology mesh --partition_only --partitioner scan qasm/best-tfim_40_preoptimized.qasm

python qutop.py --blocksize 4 --topology mesh --partition_only --partitioner scan qasm/best-qft_64_preoptimized.qasm

python qutop.py --blocksize 4 --topology mesh --partition_only --partitioner scan qasm/best-add_65_preoptimized.qasm
