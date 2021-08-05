from bqskit.ir.lang.qasm2.qasm2 import OPENQASM2Language
from bqskit.compiler.passes.util.intermediate import RestoreIntermediatePass
from bqskit import Circuit
import pickle

#filename = "qft_5"
filename = "add_9"
coupling = "mesh_3_3"
blocksize = "blocksize_3"
#blocksize = "blocksize_4"
suffix = "greedy_shortest-path"
#suffix = "shortest-path"
num_q = 9
#name = f"{filename}_{coupling}_{blocksize}"
name = f"{filename}_{coupling}_{blocksize}"
layoutname = f"layout_qasm/{name}"
synthname  = f"synthesized_qasm/{name}_{suffix}"
mappedname = f"mapped_qasm/{name}_{suffix}"
with open(layoutname, 'r') as f:
    layout = OPENQASM2Language().decode(f.read())
with open(synthname, 'r') as f:
    synth = OPENQASM2Language().decode(f.read())
with open(mappedname, 'r') as f:
    mapp = OPENQASM2Language().decode(f.read())

layout_unitary = layout.get_unitary()
synth_unitary = synth.get_unitary()
mapp_unitary = mapp.get_unitary()

import numpy as np
print("Distance b/w layout and synth: ", layout_unitary.get_distance_from(synth_unitary))
print("Distance b/w layout and mapp: ", layout_unitary.get_distance_from(mapp_unitary))
print("Distance b/w mapp and synth: ", synth_unitary.get_distance_from(mapp_unitary))

structure_path = f"block_files/{name}_greedy/structure.pickle"
with open(structure_path, "rb") as f:
    structure = pickle.load(f)
print(structure)