from sys import argv
from os import listdir
from re import match

def count_cx(qasm_file):
	count = 0
	with open(qasm_file, "r") as f:
		for line in f.readlines():
			if match("cx", line):
				count += 1
	return count

if __name__ == "__main__":
	blocks = sorted(listdir(argv[1]))
	synths = sorted(listdir(argv[2]))
	blocks.remove("structure.pickle")
	for b in synths:
		if not b.endswith(".qasm"):
			synths.remove(b)

	string = ""
	for num in range(len(blocks)):
		orig = count_cx(f"{argv[1]}/{blocks[num]}")
		opti = count_cx(f"{argv[2]}/{synths[num]}")
		string += f"{orig}, {opti}\n"
		
	print(string)
