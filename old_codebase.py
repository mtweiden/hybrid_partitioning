from __future__ import annotations
from typing import Any, Sequence

from qsearch import (
	Project,
	leap_compiler, 
	post_processing,
	parallelizers, 
	gatesets, 
	assemblers,
	multistart_solvers
)
from util import load_block_topology, load_block_circuit
from shutil import rmtree
from os.path import exists
from psutil import cpu_count
from re import search

from numpy import ndarray

def weighted_astar(circ, v, weight, options):
	"""
	Heuristic based off astar that takes into account gateset weights.
	"""
	# Should I add weights from all layers or just the last?
	gateset_weight = 0
	gateset = options["gateset"].adjacency
	all_gates = circ._subgates
	# Physical gates are free
	gate_weights = {(e[0],e[1]): e[2]-1 for e in gateset}
	for num_layers, layer in enumerate(all_gates):
		for gate in layer.assemble(v):
			if gate[1] == "CNOT":
				gateset_weight += gate_weights[gate[3]]
	# Normalization factor is the weight if each layer uses the most expensive
	# edge. No need to normalize with number of qudits because each layer only
	# contains a single CNOT.
	normalization = options["max_gateset_weight"] * num_layers
	gateset_weight /= normalization if normalization > 1 else 1
	# Max possible value for weights in 
	astar_cost = 10.0*options.eval_func(options.target, circ.matrix(v)) + weight
	return  astar_cost + gateset_weight


def num_tasks(num_synth_procs : int) -> int:
	return max([cpu_count(logical=False)//num_synth_procs, 1])


def call_old_codebase_leap(
	unitary   : ndarray, 
	graph	 : Sequence[Sequence[int]], 
	proj_name : str,
	num_synth_procs : int = 1,
) -> str:
	# No need to reverse endianness from QASM because we are interacting with
	# unitaries produced by bqskit.
	block_name = search("block_\d+", proj_name)[0]
	project = Project(proj_name)
	project.add_compilation(block_name, unitary)
	gateset = gatesets.QubitCNOTAdjacencyList(list(graph))
	project['gateset'] = gateset
	project['compiler_class'] = leap_compiler.LeapCompiler
	project['verbosity'] = 2
	max_weight = 1
	for edge in graph:
		if edge[2] > max_weight:
			max_weight = edge[2]
	project['max_gateset_weight'] = max_weight
	project["max_synth_procs"] = num_synth_procs
	project["num_tasks"] = num_tasks(num_synth_procs)
	#project['heuristic'] = weighted_astar

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
		block_name,
		assembler=assemblers.ASSEMBLER_IBMOPENQASM
	)
	return qasm


def parse_leap_files(proj_name) -> str:
	with open(f"{proj_name}.qasm", "r") as f:
		return f.read()


def check_for_leap_files(leap_proj):
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
	qudit_group : list[int],
	options : dict[str, Any],
) -> None:
	# Get subcircuit QASM by loading checkpoint or by synthesis
	synth_dir = f"{options['synthesis_dir']}/{block_name}"
	block_path = f"{options['partition_dir']}/{block_name}.qasm"
	subtopology_path = (
		f"subtopology_files/{options['target_name']}/"
		f"{block_name}_subtopology.pickle"
	)
	if check_for_leap_files(synth_dir):
		print(f"  Loading block {block_name}")
		subcircuit_qasm = parse_leap_files(synth_dir)
	else:
		# Load subtopology
		weighted_topology = load_block_topology(subtopology_path)
		subtopology = weighted_topology.subgraph(qudit_group)
		# Get rid of weights for now
		# TODO: Add weighted edges to synthesis function
		q_map = {qudit_group[k]:k for k in range(len(qudit_group))}
		sub_edges = [
			(q_map[e[0]], q_map[e[1]], subtopology[e[0]][e[1]]["weight"]) 
			for e in subtopology.edges
		]
		# Load circuit
		subcircuit = load_block_circuit(block_path, options)
		unitary = subcircuit.get_unitary().get_numpy()
		# Synthesize
		print("Using edges: ", sub_edges)
		subcircuit_qasm = call_old_codebase_leap(
			unitary,
			sub_edges,
			synth_dir,
		)
		with open(f"{synth_dir}.qasm", "w") as f:
			f.write(subcircuit_qasm)

