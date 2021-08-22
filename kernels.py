from os import listdir
import pickle

dir = "subtopology_files/add_9_mesh_9_blocksize_4_greedy_kernel"
kernels = listdir(dir)
kernels.remove("summary.txt")

for k in sorted(kernels):
	with open(f"{dir}/{k}", "rb") as f:
		kernel = pickle.load(f)
	print(k)
	print(kernel)
	print()