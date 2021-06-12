"""This script is contains a simple use case of the QFAST synthesis method."""
from __future__ import annotations

import logging

from scipy.stats import unitary_group
from scipy.stats.morestats import circmean

from bqskit.compiler import CompilationTask
from bqskit.compiler import Compiler
from bqskit.compiler.passes.synthesis import QFASTDecompositionPass
from bqskit.compiler.passes.synthesis import QSearchSynthesisPass
from bqskit.ir import Circuit
from bqskit.ir.lang.qasm2.qasm2 import OPENQASM2Language
from bqskit.compiler.passes.foreachblockpass import ForEachBlockPass
from bqskit.compiler.machine import MachineModel
from bqskit.compiler.passes.simplepartitioner import SimplePartitioner

from bqskit.ir.gates.constant.cx import CNOTGate
from bqskit.ir.gates.constant.h import HGate


if __name__ == '__main__':
    # Enable logging
    logging.getLogger('bqskit').setLevel(logging.DEBUG)

    # Let's import a 5 qudit unitary to synthesize.
    #with open('scratch/qft_qasm/qft_5.qasm', 'r') as f:
    #    circuit = OPENQASM2Language().decode(f.read())
    circuit = Circuit(5)
    circuit.append_gate(CNOTGate(), [0,1])
    circuit.append_gate(HGate(), [1])
    circuit.append_gate(CNOTGate(), [0,1])
    circuit.append_gate(HGate(), [0])
    circuit.append_gate(HGate(), [0])
    circuit.append_gate(HGate(), [1])
    circuit.append_gate(HGate(), [1])

    # Do partitioning
    machine = MachineModel(5)
    partitioner = SimplePartitioner(machine, 3)

    # Combine all passes
    passes = [ partitioner, QSearchSynthesisPass()]
    #passes = [QSearchSynthesisPass()]

    # We will now define the CompilationTask we want to run.
    task = CompilationTask(circuit, passes)

    # Finally let's create create the compiler and execute the CompilationTask.
    with Compiler() as compiler:
        compiled_circuit = compiler.compile(task)
        for op in compiled_circuit:
            print(op)
        new_qasm = OPENQASM2Language().encode(compiled_circuit)

    with open('scratch/new_qasm.qasm', 'w') as f:
        f.write(new_qasm)
