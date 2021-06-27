from __future__ import annotations
from typing import Any
import pickle

from bqskit import Circuit
from bqskit.ir.lang.qasm2.qasm2	import OPENQASM2Language

def get_block(
	block_path : str,
	options : dict[str, Any]
) -> Circuit:
	if options['is_qasm']:
		with open(block_path, "r") as f:
			return OPENQASM2Language().decode(f.read())
	else:
		with open(block_path, 'rb') as f:
			return pickle.load(f)