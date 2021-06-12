Starting with the assumption that the circuit has been logically optimized.

Use QISKIT to get a layout for the circuit.

Using this layout, create a new `hybrid topology`
	Leave in physical links
	Add logical links for unperformable gates
		Logical links should be added so that they connect to the qubit group
		according to which insider qubit has the shortest graph distance

Run partitioning/synthesis on this new hybrid topology

Use QISKIT transpiler to get mapping for the circuit

Run partitioning/synthesis on the physically mapped circuit


