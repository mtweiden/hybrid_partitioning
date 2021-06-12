from bqskit.ir.lang.qasm2.qasm2 import OPENQASM2Language
from bqskit import Circuit

from scipy.linalg import norm

with open("synthesized_qasm/qft_5_mesh_3_3_blocksize_3_shortestpath", 'r') as f:
    original = OPENQASM2Language().decode(f.read())
with open("synthesized_qasm/qft_5_mesh_3_3_blocksize_3_reuseedges", 'r') as f:
    synthesized = OPENQASM2Language().decode(f.read())

num_q = 9

original_unitary     = original.get_unitary().get_numpy()
synthesized_unitary  = synthesized.get_unitary().get_numpy()

import numpy as np
np.set_printoptions(formatter={'complex_kind': "{0:.3f}".format})

for i in range(2**num_q):
    for j in range(2**num_q):
        if abs(original_unitary[i][j] + synthesized_unitary[i][j]) > 1e-7:
            print("(%d,%d)"%(i,j), original_unitary[i][j], "    ", synthesized_unitary[i][j])

print(norm(original_unitary - synthesized_unitary))