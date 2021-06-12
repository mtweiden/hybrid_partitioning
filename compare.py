from os import walk
from re import match
from qiskit import QuantumCircuit, execute, Aer
from scipy.linalg import norm

# Find the original circuit in the qasm/ directory
_, _, qasm_filenames = next(walk('qasm/'))

# See if there is a version of the same circuit in the mapped_qasm/ directory
_, _, mapped_filenames = next(walk('mapped_qasm/'))

exists_flag = False
error_flag = False
base_unitary = None
backend = Aer.get_backend("unitary_simulator")
for qasm_file in qasm_filenames:
	circ_name = qasm_file.split('.qasm')[0]
	base_circ = QuantumCircuit.from_qasm_file("qasm/" + qasm_file)
	
	# Unitaries are different sizes because the number of physical qudits is 
	# often larger than the number of logical qudits
	#error_flag = base_circ.num_qubits < 12
	if error_flag:
		base_unitary = execute(base_circ, backend).result().get_unitary(base_circ)
	base_counts = base_circ.count_ops()
	string = "Base circuit: " + circ_name + "\n"
	for op_type in base_counts.keys():
		string += (str(op_type) + ": " + str(base_counts[op_type]) + "\n")

	for mapped_file in mapped_filenames:
		if match(circ_name, mapped_file):
			exists_flag = True
			circ = QuantumCircuit.from_qasm_file("mapped_qasm/" + mapped_file)
			counts = circ.count_ops()
			string += mapped_file + "\n"
			for op_type in counts.keys():
				string += (str(op_type) + ": " + str(counts[op_type]) + "\n")
			if error_flag:
				synth_unitary = execute(circ, backend).result().get_unitary(circ)
				print("Error: %f" %(norm(base_unitary - synth_unitary)))
	if exists_flag:
		print(string)
		flag = False
