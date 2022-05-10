import argparse
from os import listdir
from bqskit import Circuit
from bqskit.ir.gates.constant.cx import CNOTGate
from topology import kernel_type
import pickle

if __name__ == '__main__':
	"""
	NOTE: Only support blocksize 4 right now
	"""

	parser = argparse.ArgumentParser()
	parser.add_argument("benchmark", type=str)
	args = parser.parse_args()

	benchmark = args.benchmark.split('/')[-1]
	if '-' in benchmark:
		benchmark = benchmark.split('-')[-1]
	print(benchmark)

	# put block_files/ subdirectory as benchmark input
	benchmark_base  = f'block_files/{benchmark}'
	benchmark_lines = f'synthesis_files/lines-{benchmark}_kernel'
	benchmark_stars = f'synthesis_files/stars-{benchmark}_kernel'
	benchmark_rings = f'synthesis_files/rings-{benchmark}_kernel'
	benchmark_kites = f'synthesis_files/kites-{benchmark}_kernel'
	benchmark_thetas = f'synthesis_files/thetas-{benchmark}_kernel'
	benchmark_alls  = f'synthesis_files/alls-{benchmark}_kernel'

	cnots_base  = []
	cnots_lines = []	
	cnots_stars = []
	cnots_rings = []
	cnots_kites = []
	cnots_thetas = []
	cnots_alls  = []

	kernel_base = []

	blocks = sorted(listdir(f'{benchmark_base}'))
	for block in reversed(blocks):
		if '.qasm' not in block:
			blocks.remove(block)

	for block in blocks:
		circuit_base  = Circuit.from_file(f'{benchmark_base}/{block}') 
		circuit_lines = Circuit.from_file(f'{benchmark_lines}/{block}')
		circuit_stars = Circuit.from_file(f'{benchmark_stars}/{block}')
		circuit_rings = Circuit.from_file(f'{benchmark_rings}/{block}')
		circuit_kites = Circuit.from_file(f'{benchmark_kites}/{block}')
		circuit_thetas = Circuit.from_file(f'{benchmark_thetas}/{block}')
		circuit_alls  = Circuit.from_file(f'{benchmark_alls}/{block}')

		cnots_base.append(circuit_base.count(CNOTGate()))  
		cnots_lines.append(circuit_lines.count(CNOTGate()))
		cnots_stars.append(circuit_stars.count(CNOTGate()))
		cnots_rings.append(circuit_rings.count(CNOTGate()))
		cnots_kites.append(circuit_kites.count(CNOTGate()))
		cnots_thetas.append(circuit_thetas.count(CNOTGate()))
		cnots_alls.append(circuit_alls.count(CNOTGate()))


		# See what kernel was picked by the similarity function
		# Note: much better to just load the subtopology files
		#edges = set([])
		#for op in circuit_base:
		#	if len(op.location) == 2:
		#		edges.add(op.location)
		with open(f'subtopology_files/{benchmark}_kernel/{block.split(".qasm")[0]}_kernel.pickle', 'rb') as f:
			edges = pickle.load(f)
		kernel_base.append(kernel_type(edges, 4))

	kernels = ('line', 'star', 'ring', 'kite', 'theta', 'all')
	#kernels = ('line', 'star', 'ring')
	score = 0
	for i in range(len(blocks)):
		cnots = (cnots_lines[i], cnots_stars[i], cnots_rings[i], cnots_kites[i], cnots_thetas[i], cnots_alls[i])
		#cnots = (cnots_lines[i], cnots_stars[i], cnots_rings[i])

		# See what kernel resulted in the circuit with the fewest cnots
		min_cnots = min(cnots)
		best_kernel = [kernels[k] for k in range(len(kernels)) if cnots[k] == min_cnots]
		
		selected_kernel = kernel_base[i].split('-')[-1]
		if selected_kernel in best_kernel:
			score += 1

		print(f'selected-{kernel_base[i]}, best-{best_kernel}')

	score /= len(blocks)
	print(score)
		


