from __future__ import annotations
from os.path import exists
from os import mkdir, listdir
import argparse
from post_synth import replace_blocks

from topology import run_stats_dict
from stas import setup_args

from util import setup_options

import pandas as pd
import numpy as np

# Enable logging
import logging
logging.getLogger('bqskit').setLevel(logging.INFO)

PARTITION_SCORES = [1, 4, 12, 28, 24, 8]

GET_PARTITION_DATA = True

if __name__ == '__main__':
    args =  setup_args(need_qasm=False)

    qasms = listdir("mapped_qasm")
    rows = []

    for qasm in qasms:
        if "remapped" in qasm:
            continue
        # grab args from name
        name_arr = qasm.split("_")
        args.qasm_file = "qasm/" + "_".join(name_arr[0:2]) + ".qasm"
        args.blocksize = int(name_arr[5])
        args.map_type = name_arr[2]
        args.partitioner = name_arr[6]
        args.router = name_arr[8].replace(".qasm", "")
        options = setup_options(args.qasm_file, args)
        pre = run_stats_dict(options, post_stats=False)
        post = run_stats_dict(options, post_stats=True)
        if not exists(options["remapped_qasm_file"]):
            replace_blocks(options)
        replace = run_stats_dict(options, resynthesized=True)

        all = [pre,post, replace]

        results = [post, replace]

        for data in all:
            data["name"] = "_".join(name_arr[0:2])
            data["blocksize"] = args.blocksize
            data["topology"] = args.map_type

        best_cnots = post["Total CNOTs"]

        empty = pre.get("empty", 0)
        two_line = pre.get("2-line", 0)
        three_line = pre.get("3-line", 0)
        four_line = pre.get("4-line", 0)
        four_star = pre.get("4-star", 0)
        four_ring = pre.get("4-ring", 0)

        partitions = [empty, two_line, three_line, four_line, four_star, four_ring]

        total_partitions = sum(partitions)

        total_four_blocks = sum(partitions[-3:])

        routability_score_all = np.dot(partitions, PARTITION_SCORES) / total_partitions

        routability_score_fours = np.dot(partitions[-3:], PARTITION_SCORES[-3:]) / total_four_blocks


        if GET_PARTITION_DATA:
            routability_data = {}
            routability_data["name"] = "_".join(name_arr[0:2])
            routability_data["Total CNOTs"] = best_cnots
            routability_data["routability_score_all_blocks"] = routability_score_all
            routability_data["routability_score_four_blocks"] = routability_score_fours
            rows.append(routability_data)
        else:
            rows.extend(all)

        print( "_".join(name_arr[0:2]))

    full_data = pd.DataFrame.from_dict(rows, orient='columns')

    full_data.to_csv("out.csv")
