# Qiskit dependencies
from qiskit import QuantumCircuit
from qiskit.transpiler import CouplingMap
from qiskit.transpiler.passes import SabreLayout, SabreSwap
from qiskit.transpiler.passmanager import PassManager
# Standard dependencies
from math import ceil, sqrt
from re import match, findall
from sys import argv
# Project dependiences
from coupling import get_coupling_map
from qasm_mapping import format


def find_num_qudits(
	input_qasm_file : str,
) -> int:
	with open(input_qasm_file, 'r') as f:
		for line in f:
			if match("qreg ", line):
				num_logical = int(findall("\d+",line)[0])
				break
	return num_logical


def do_layout(input_qasm_file, coupling_map_file, output_qasm_file):

	# Gather circuit data
	circ = QuantumCircuit.from_qasm_file(input_qasm_file)
	num_logical_qubits = circ.width()
	(num_q, coupling_graph) = get_coupling_map(coupling_map_file, 
		num_logical_qubits, make_coupling_map_flag=True)

	# Set up Passes
	seed = 42
	layout = SabreLayout(
		coupling_map=CouplingMap(list(coupling_graph)),
		seed=seed,
		routing_pass=None,
		max_iterations=25
	)

	pass_man = PassManager([layout])

	# Create circuit with new layout and layout dictionary
	new_circ = pass_man.run(circ)
	qiskit_map = layout.property_set['layout'].get_virtual_bits()
	l2p_map = {l.index: qiskit_map[l] for l in qiskit_map}

	# Qiskit doesn't use physical numbering in the qasm() method, so parse the qasm
	# file and do the mapping here.
	with open(input_qasm_file, 'r') as in_qasm:
		with open(output_qasm_file, 'w') as out_qasm:
			for line in in_qasm:
				if match('qreg q\[\d+\];', line):
					out_qasm.write('qreg q[%d];\n' %(num_q))
				else:
					out_qasm.write(format(line, l2p_map))


def do_routing(input_qasm_file, coupling_map_file, output_qasm_file):

	# Gather circuit data
	circ = QuantumCircuit.from_qasm_file(input_qasm_file)
	(num_q, coupling_graph) = get_coupling_map(coupling_map_file)

	# Set up Passes
	seed = 42
	router = SabreSwap(
		coupling_map=CouplingMap(list(coupling_graph)),
		heuristic='lookahead',
		seed=seed
	)
	pass_man = PassManager([router])

	# Create circuit with new layout and layout dictionary
	new_circ = pass_man.run(circ)
	new_qasm = new_circ.qasm()

	with open(output_qasm_file, 'w') as out_qasm:
		out_qasm.write(new_qasm)

def dummy_layout(input_qasm_file, coupling_map_file, output_qasm_file):
	with open(input_qasm_file, 'r') as in_qasm:
		with open(output_qasm_file, 'w') as out_qasm:
			out_qasm.write(in_qasm.read())


def dummy_routing(input_qasm_file, coupling_map_file, output_qasm_file):
	with open(input_qasm_file, 'r') as in_qasm:
		with open(output_qasm_file, 'w') as out_qasm:
			out_qasm.write(in_qasm.read())

if __name__ == "__main__":
	if len(argv) != 3:
		print("Missing arguments")
		print(">>> python3 mapping <qasm file> <linear | mesh | alltoall>")
		quit
	else:
		do_layout(argv[1], argv[2])