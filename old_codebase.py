from __future__ import annotations
from typing import Sequence

from qsearch import (
	unitaries, Project,
	leap_compiler, post_processing,
	parallelizers, 
	gatesets, assemblers,
	multistart_solvers
)
from shutil import rmtree
from re import match, search
from os.path import exists

from qasm_mapping import format
from numpy import ndarray


def call_old_codebase_leap(
	unitary   : ndarray, 
	graph	 : Sequence[Sequence[int]], 
	proj_name : str,
	layout_map : dict[int,int]
) -> str:
	# Convert to unitary
	#unitary = endian_reverse(unitary)
	# Create project and set up
	project = Project('leap_files/' + proj_name)
	project.add_compilation(proj_name, unitary)
	gateset = gatesets.QubitCNOTAdjacencyList(list(graph))
	project['gateset'] = gateset
	project['compiler_class'] = leap_compiler.LeapCompiler
	project['verbosity'] = 2

	# Run
	project.run()
	# Post processing
	project.post_process(
		post_processing.LEAPReoptimizing_PostProcessor(),
		solver = multistart_solvers.MultiStart_Solver(8),
		parallelizer = parallelizers.ProcessPoolParallelizer,
		weight_limit = 5
	)
	qasm = project.assemble(
		proj_name,
		assembler=assemblers.ASSEMBLER_IBMOPENQASM
	)
	qasm_str = ""
	qasm_list = qasm.split('\n')
	formatted_qasm_list = []
	for qasm_line in qasm_list:
		if not match('OPENQASM', qasm_line) and not match('include', qasm_line)\
			and not match('qreg', qasm_line):
			formatted_qasm_list.append(format(qasm_line, layout_map))
	for line in formatted_qasm_list:
		qasm_str += line + '\n'
	return qasm_str


def parse_leap_files(proj_name, layout_map) -> str:
	project = Project("leap_files/" + proj_name)
	qasm = project.assemble(
		proj_name,
		assembler=assemblers.ASSEMBLER_IBMOPENQASM
	)
	qasm_str = ""
	qasm_list = qasm.split('\n')
	formatted_qasm_list = []
	for qasm_line in qasm_list:
		if not match('OPENQASM', qasm_line) and not match('include', qasm_line)\
			and not match('qreg', qasm_line):
			formatted_qasm_list.append(format(qasm_line, layout_map))
	for line in formatted_qasm_list:
		qasm_str += line + '\n'
	return qasm_str
	


def check_for_leap_files(leap_proj):
	"""
	If the leap project was previously completed, return true.

	Args:
		Project to check for in the leap_files directory.
	"""
	if not exists("leap_files/" + leap_proj):
		return False
	# If finished postprocessing, return True
	with open("leap_files/"+leap_proj+"/"+leap_proj + "-project-log.txt") as f:
		for line in f:
			if search("Finished postprocessing", line):
				return True
	# If exited the loop, delete the directory and return false.
	rmtree("leap_files/" + leap_proj)
	return False
