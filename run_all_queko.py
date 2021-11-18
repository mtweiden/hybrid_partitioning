import os
import numpy as np
import glob

# Running queko benchmarks on sycamore

if __name__=="__main__":
    # dir_name = argv[1]
    dir_name = "BSS"

    full_dir = os.path.join("qasm", "54*.qasm")

    files = glob.glob(full_dir)

    prng = np.random.RandomState(1234)

    selected = prng.choice(files, size=5)

    for fil_name in selected:
        parts = fil_name.split("_")
        optimal_depth = int(parts[1].replace("CYC", ""))

        if "900" in fil_name:
            flag = ""
        else:
            flag = "--partition_only "
            continue

        cmd = "python stas.py {} --blocksize=4 {}--topology sycamore".format(fil_name, flag)

        print(cmd)
        os.system(cmd)

