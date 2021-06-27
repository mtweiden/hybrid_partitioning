from bqskit.ir.lang.qasm2.qasm2 import OPENQASM2Language
from bqskit.compiler.passes.util.intermediate import RestoreIntermediatePass
from bqskit import Circuit
import pickle

filename = "mult_8"
coupling = "mesh_3_3"
blocksize = "blocksize_5"
num_q = 9

layoutname = f"layout_qasm/{filename}_{coupling}"
synthname  = f"synthesized_qasm/{filename}_{coupling}_{blocksize}"
mappedname = f"mapped_qasm/{filename}_{coupling}_{blocksize}"
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

structure_path = f"block_files/{filename}_{coupling}_{blocksize}/structure.pickle"
with open(structure_path, "rb") as f:
    structure = pickle.load(f)
print(structure)