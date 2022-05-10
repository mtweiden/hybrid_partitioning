from bqskit.ir.circuit import Circuit
import argparse
import pickle
from os import listdir
from re import findall

from bqskit.ir.gates.circuitgate import CircuitGate

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("blocks_dir", type=str) 
	args = parser.parse_args()

	if args.blocks_dir.endswith('/'):
		blocks_dir = args.blocks_dir[0:-1]
	else:
		blocks_dir = args.blocks_dir
	with open(f"{blocks_dir}/structure.pickle", "rb") as f:
		structure = pickle.load(f)
	
	# Find number of qubits in circuit
	if "mesh" in blocks_dir:
		topology = findall("mesh_\d+", blocks_dir)[0]
	elif "falcon" in blocks_dir:
		topology = findall("falcon_\d+", blocks_dir)[0]
	elif "linear" in blocks_dir:
		topology = findall("linear_\d+", blocks_dir)[0]

	num_qubits = int(findall("\d+", topology)[0])

	block_files = [f for f in sorted(listdir(blocks_dir)) if f.endswith(".qasm")]

	circuit = Circuit(num_qubits)
	for block_num in range(len(block_files)):
		subcircuit = Circuit(len(structure[block_num])).from_file(f"{blocks_dir}/{block_files[block_num]}")

		# Handle the case where the circuit is still smaller than the qudit
		# group, should only happen on circuits synthesized in an older
		# version.
		group_len = subcircuit.num_qudits
		qudit_group = [structure[block_num][x] for x in range(group_len)]
		subcircuit = CircuitGate(subcircuit)
		circuit.append_gate(subcircuit, qudit_group)
	
	partitioned_circ = f"partitioned_circuits/{blocks_dir.split('/')[-1]}.pickle"
	with open(partitioned_circ, "wb") as f:
		pickle.dump(circuit, f)
	for op in circuit:
		print(op)

