from __future__ import annotations
from typing import Any, Sequence
from bqskit.compiler.compiler import Compiler

from bqskit.compiler.machine import MachineModel

from util import load_block_topology, load_block_circuit
from shutil import rmtree
from os.path import exists
from psutil import cpu_count
from re import search

from numpy import ndarray

from bqskit import CompilationTask
#from bqskit.compiler.passes.synthesis.qsearch import QSearchSynthesisPass
from bqskit.compiler.passes.synthesis.old_leap import OldLeap
#from bqskit.compiler.passes.synthesis.old_leap import synthesize_unitary
from bqskit.compiler.passes.synthesis.qfast import QFASTDecompositionPass
from bqskit.compiler.passes.synthesis.qpredict import QPredictDecompositionPass
from bqskit.compiler.passes.util.converttou3 import VariableToU3Pass
from bqskit.ir.lang.qasm2.qasm2 import OPENQASM2Language


def num_tasks(num_synth_procs : int) -> int:
	return max([cpu_count(logical=False)//num_synth_procs, 1])


def parse_synthesis_files(proj_name) -> str:
	with open(f"{proj_name}.qasm", "r") as f:
		return f.read()


def check_for_synthesis_files(leap_proj):
	"""
	If the leap project was previously completed, return true.
	Args:
		Project to check for in the leap_files directory.
	"""
	if not exists(f"{leap_proj}.qasm"):
		if exists(f"{leap_proj}"):
			rmtree(f"{leap_proj}")
		return False
	else:
		return True


def synthesize(
	block_name : str,
	qudit_group : Sequence[int],
	options : dict[str, Any],
) -> None:
	# Get subcircuit QASM by loading checkpoint or by synthesis
	synth_dir = f"{options['synthesis_dir']}/{block_name}"
	block_path = f"{options['partition_dir']}/{block_name}.qasm"
	subtopology_path = (
		f"subtopology_files/{options['target_name']}/"
		f"{block_name}_kernel.pickle"
	)
	if check_for_synthesis_files(synth_dir):
		print(f"  Loading block {block_name}")
		subcircuit_qasm = parse_synthesis_files(synth_dir)
	else:
		# Load subtopology edge set
		subtopology = load_block_topology(subtopology_path)
		# Set up machine model
		model = MachineModel(len(qudit_group), subtopology)
		data = {"machine_model": model}
		# Load circuit
		subcircuit = load_block_circuit(block_path, options)
		#unitary = subcircuit.get_unitary().get_numpy()
		task = CompilationTask(subcircuit, [QFASTDecompositionPass()])
		# Synthesize
		print("Using edges: ", subtopology)
		if options["decomposer"] == "qpredict":
			QPredictDecompositionPass().run(subcircuit, data)
		elif options["decomposer"] == "qfast":
			QFASTDecompositionPass().run(subcircuit, data)
		#QSearchSynthesisPass().run(subcircuit, data)
		#VariableToU3Pass().run(subcircuit, {})
		#subcircuit_qasm = OPENQASM2Language().encode(subcircuit)

		subcircuit_qasm = OldLeap().run(subcircuit, data)
		VariableToU3Pass().run(subcircuit, {})
		subcircuit_qasm = OPENQASM2Language().encode(subcircuit)

		#subcircuit_qasm = synthesize_unitary(subcircuit.get_unitary(), data)
		with open(f"{synth_dir}.qasm", "w") as f:
			f.write(subcircuit_qasm)

