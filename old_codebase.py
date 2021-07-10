from __future__ import annotations
from typing import Sequence

from qsearch import (
	Project,
	leap_compiler, 
	post_processing,
	parallelizers, 
	gatesets, 
	assemblers,
	multistart_solvers
)
from shutil import rmtree
from re import match, findall
from os.path import exists

from numpy import ndarray


def call_old_codebase_leap(
	unitary   : ndarray, 
	graph	 : Sequence[Sequence[int]], 
	proj_name : str,
) -> str:
	# Convert to unitary
	#unitary = endian_reverse(unitary)
	# Create project and set up
	project = Project('synthesis_files/' + proj_name)
	project.add_compilation(proj_name, unitary)
	gateset = gatesets.QubitCNOTAdjacencyList(list(graph))
	project['gateset'] = gateset
	project['compiler_class'] = leap_compiler.LeapCompiler
	project['verbosity'] = 2

	# Run
	project.run()
	# Post processing
	#project.post_process(
	#	post_processing.LEAPReoptimizing_PostProcessor(),
	#	solver = multistart_solvers.MultiStart_Solver(8),
	#	parallelizer = parallelizers.ProcessPoolParallelizer,
	#	weight_limit = 5
	#)
	qasm = project.assemble(
		proj_name,
		assembler=assemblers.ASSEMBLER_IBMOPENQASM
	)
	return qasm


def parse_leap_files(proj_name) -> str:
	project = f"synthesis_files/{proj_name}.qasm"
	with open(project, "r") as f:
		return f.read()


def check_for_leap_files(leap_proj):
	"""
	If the leap project was previously completed, return true.
	Args:
		Project to check for in the leap_files directory.
	"""
	if not exists(f"synthesis_files/{leap_proj}.qasm"):
		if exists(f"synthesis_files/{leap_proj}"):
			rmtree(f"synthesis_files/{leap_proj}")
		return False
	else:
		return True


def format(input_line, layout_map) -> str:
    """
    Returns new qasm line with physical qubit numbering.

    Args:
        input_line (str): Original qasm string.

        layout_map (dict): Logical to physical mapping.
    
    Returns:
        qasm_str (str): Newly mapped qasm string.

    Note:
        Assumes there is a single register named 'q', replaces that name with 
        'physical'.
    """
    # Find all instances of qubit reference
    if match('qreg', input_line):
        return input_line.replace('q[', 'physical[')

    qasm_str = input_line

    log_qubits = list(findall('q\[\d+\]', input_line))
    for lq in log_qubits:
        log_number = int(findall('\d+', lq)[0])
        replacement = 'physical[' + str(layout_map[log_number]) + ']'
        qasm_str = qasm_str.replace(lq, replacement)
        
    return qasm_str.replace('physical[', 'q[')


if __name__ == '__main__':
    str1 = "cx q[0], q[1];"
    str2 = "u3(0,0,-pi/4)  q[100];"
    str3 = ""

    mapping = {0:'a', 1:'b', 100:'c'}

    print(format(str1, mapping))
    print(format(str2, mapping))