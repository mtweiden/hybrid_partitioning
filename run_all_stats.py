from __future__ import annotations
from os.path import exists
from os import mkdir, listdir
import argparse
from post_synth import replace_blocks

from topology import run_stats_dict
from stas import setup_args, save_dict, get_saved_dict

from util import setup_options

import pandas as pd
import numpy as np
import json

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
        test_name = "_".join(name_arr[0:-7])
        topology = name_arr[-7]
        blocksize = name_arr[-4]
        partitioner = name_arr[-3]
        args.qasm_file = "qasm/" + test_name + ".qasm"
        args.blocksize = int(blocksize)
        args.map_type = topology
        args.partitioner = partitioner
        args.router = name_arr[-1].replace(".qasm", "")
        options = setup_options(args.qasm_file, args)

        pre = get_saved_dict(options, "pre")

        print(test_name)
        if pre is None:
            print("Running PREEEE")
            pre = run_stats_dict(options, post_stats=False)
        
        post = get_saved_dict(options, "post")
            
        if post is None: 
            post = run_stats_dict(options, post_stats=True)

        all = [pre, post]
        if not GET_PARTITION_DATA:
            replace = get_saved_dict(options, "replace")
            if replace is None:
                if not exists(options["remapped_qasm_file"]):
                    replace_blocks(options)
                replace = run_stats_dict(options, resynthesized=True)
            all = [pre,post, replace]

        for data in all:
            data["name"] = test_name
            data["blocksize"] = args.blocksize
            data["topology"] = args.map_type

        best_swaps= post["SWAPs from routing"]
        best_cnots = post["Total CNOTs"]
        best_4_block_cnots = post["Total 4-block CNOTs"]

        print(best_cnots)
        print(best_4_block_cnots)

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
            routability_data["name"] = test_name
            routability_data["Average Swaps"] = best_swaps / total_partitions
            routability_data["Average CNOTs"] = best_cnots / total_partitions
            routability_data["Average 4-block CNOTs"] = best_4_block_cnots / total_four_blocks
            routability_data["routability_score_all_blocks"] = routability_score_all
            routability_data["routability_score_four_blocks"] = routability_score_fours
            rows.append(routability_data)
        else:
            rows.extend(all)

    full_data = pd.DataFrame.from_dict(rows, orient='columns')

    full_data.to_csv("out_routability.csv")
