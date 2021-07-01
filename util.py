from __future__ import annotations
from typing import Any, Sequence
import pickle

from bqskit import Circuit
from bqskit.ir.gates.circuitgate import CircuitGate
from bqskit.ir.lang.qasm2.qasm2	import OPENQASM2Language
from bqskit.ir.region import CircuitRegion, CircuitRegionLike

def load_block_circuit(
	block_path : str,
	options : dict[str, Any]
) -> Circuit:
	if options['is_qasm']:
		with open(block_path, "r") as f:
			return OPENQASM2Language().decode(f.read())
	else:
		with open(block_path, 'rb') as f:
			return pickle.load(f)


def load_block_topology(
	block_path : str,
) -> Sequence[Sequence[int]]:
	with open(block_path, "rb") as f:
		return pickle.load(f)


def save_block_topology(
	subtopology_edge_set: Sequence[Sequence[int]],
	block_path : str,
) -> None:
	with open(block_path, 'wb') as f:
		pickle.dump(subtopology_edge_set, f)


def load_circuit_structure(
	partition_directory : str,
) -> Sequence[Sequence[int]]:
	with open(f"{partition_directory}/structure.pickle", "rb") as f:
		return pickle.load(f)


def careful_fold(
	circuit : Circuit,
) -> Circuit:
	"""
	Needed for maintaining CircuitGate sizes.

	Args:
		circuit (Circuit): Circuit to be folded.

	Returns:
		Circuit: The CircuitGate version of `circuit`.
	"""
	region = CircuitRegion({q: (0, circuit.get_depth() - 1) 
		for q in range(circuit.get_size())})
	folded_circuit = Circuit(circuit.get_size(), circuit.get_radixes())
	small_region = circuit.downsize_region(region)
	cgc = circuit.get_slice(small_region.points)
	if len(region.location) > len(small_region.location):
		for i in range(len(region.location)):
			if region.location[i] not in small_region.location:
				cgc.insert_qudit(i)
	folded_circuit.append_gate(
		CircuitGate(cgc, True),
		sorted(list(region.keys())),
		list(cgc.get_params()),
	)
	return folded_circuit
