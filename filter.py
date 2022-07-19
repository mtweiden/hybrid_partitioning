"""
Compare synthesized and unsynthesized blocks of a circuit, replace the 
synthesized blocks with the original blocks if they are expected to hurt the
overall performance of a circuit.
"""
import argparse
import os
import bqskit
from topology import kernel_type
from bqskit.ir.gates.constant.cx import CNOTGate


def score_connectivity(circuit):
	"""
	0 : 'discon'
	1 : 'line'
	2 : 'star'
	3 : 'ring'
	4 : 'kite'
	5 : 'theta'
	6 : 'all'
	"""
	edges= set([])
	for op in circuit:
		if len(op.location) == 2:
			edges.add(op.location)
	
	# line < star < ring < kite < theta < alls
	tops = ('discon', 'line', 'star', 'ring', 'kite', 'theta', 'all')
	type = kernel_type(edges, circuit.num_qudits)

	top_score = 6
	for score, t in enumerate(tops):
		if t in type:
			top_score = score

	return top_score


def check_if_should_substitute(
	synth_cnots, synth_score, original_cnots, original_score
) -> bool:
	"""
	If topologies are the same, number of CNOTs determines block should be
	chosen.

	Otherwise, lines and stars are considered the same difficulty. Rings are a
	little bit harder. Kites and thetas are both difficult. Alls are the 
	hardest. If a block was reduced enough with a more complex block, pick it
	anyways.

	For each 'step up' in complexity of topologies, we need to see at least a
	certain percentage improvement.
	line or star -> ring - 10% 
	line or star -> kite or theta - 20% 
	line or star -> alls - 30% 

	True: substitute out for original block
	False: leave synthesized block in
	"""
	if synth_cnots == original_cnots == 0:
		return False 
	
	diff_ratio = abs(synth_cnots - original_cnots) / max(synth_cnots, original_cnots)

	# If there's a small diference
	#if diff_ratio < 0.05:
	#if diff_ratio < 0.2:
	if diff_ratio < 0.3:
		# Return which ever is simpler
		return synth_score > original_score # Replace if original simpler
	# Medium difference
	#elif diff_ratio < 0.15:
	#elif diff_ratio < 0.25:
	#elif diff_ratio < 0.30: # Changed for more restrictive topology
	elif diff_ratio < 0.4:
		# If fewer in synth 
		if synth_cnots <= original_cnots:
			# Almost always return False
			return synth_score - 3 > original_score
		# If fewer in original
		else:
			# Almost always return True
			return synth_score - 3 < original_score
	# Big difference
	else:
		return synth_cnots > original_cnots


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('block_files', type=str)
	parser.add_argument('synth_files', type=str)
	args = parser.parse_args()

	block_files = [x for x in sorted(os.listdir(args.block_files)) if x.endswith('.qasm')]
	synth_files = [x for x in sorted(os.listdir(args.synth_files)) if x.endswith('.qasm')]

	# Only work with finished circuits
	if len(block_files) != len(synth_files):
		raise RuntimeError(
			f'Number of block files ({len(block_files)}) is not equal to'
			f' the number of synthesis files ({len(synth_files)}).'
		)
	# Make necessary directories
	if not args.synth_files.endswith('/'):
		original_name = args.synth_files.split('/')[-1]
		synth_dir = f"synthesis_files/{args.synth_files.split('/')[-1]}"
	else:
		original_name = args.synth_files.split('/')[-2]
		synth_dir = f"synthesis_files/{args.synth_files.split('/')[-2]}"
	if not args.block_files.endswith('/'):
		block_dir = f"block_files/{args.block_files.split('/')[-1]}"
	else:
		block_dir = f"block_files/{args.block_files.split('/')[-2]}"
	
	substitued_name = f'synthesis_files/substituted-{original_name}'
	if not os.path.exists(substitued_name):
		os.mkdir(substitued_name)
	
	# Pick the block that we think will do better in the final circuit
	for i in range(len(block_files)):
		o_circuit = bqskit.Circuit(1).from_file(f'{block_dir}/{block_files[i]}')
		s_circuit = bqskit.Circuit(1).from_file(f'{synth_dir}/{synth_files[i]}')
		o_cnots = o_circuit.count(CNOTGate())
		s_cnots = s_circuit.count(CNOTGate())
		
		# Use score and number of cnots to determine which block to use
		o_score = score_connectivity(o_circuit)
		s_score = score_connectivity(s_circuit)

		# Selection function:
		selected = f'{synth_dir}/{synth_files[i]}'
		if check_if_should_substitute(s_cnots, s_score, o_cnots, o_score):
			selected = f'{block_dir}/{block_files[i]}'

		with open(selected, 'r') as input_f:
			with open(f'{substitued_name}/{block_files[i]}', 'w') as output_f:
				output_f.write(input_f.read())
