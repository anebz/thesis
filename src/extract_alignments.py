#!/usr/bin/env python3
import os
import sys
from os.path import join

# import global variables from settings.py
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from settings import *


def create_parallel_text(corpusfile: list, vocab_size: int, i: int):
    with open(join(bpedir, 'segmentations', f"{target}_{vocab_size}{'_'+str(i) if params[target]['dropout'] > 0 else ''}.bpe"), encoding='utf-8') as target_bpe:
        with open(join(bpedir, mode, f"{vocab_size}_{i}.txt"), "w") as pfile:
            for sl, tl in zip(corpusfile, target_bpe):
                pfile.write(f"{sl} ||| {tl}")
    return


def create_fwd_rev_files(outpath: str):
    if mode == "fastalign":
        os.system(f"{fastalign_path} -i {outpath}.txt -v -d -o > {outpath}.fwd")
        os.system(f"{fastalign_path} -i {outpath}.txt -v -d -o -r > {outpath}.rev")
    elif mode == "eflomal":
        os.system(f"cd {eflomal_path}; python align.py -i {outpath}.txt --model 3 -f {outpath}.fwd -r {outpath}.rev")
    return


def create_gdfa_file(outpath: str):
    # create gdfa file from .fwd and .rev
    os.system(f"{atools_path} -i {outpath}.fwd -j {outpath}.rev -c grow-diag-final-and > {outpath}_unnum.gdfa")

    # parse _unnum.gdfa to .gdfa with "\t" separator
    with open(f"{outpath}_unnum.gdfa", "r", "utf-8") as fi:
        with open(f"{outpath}.gdfa", "w", "utf-8") as fo:
            for ii, line in enumerate(fi):
                fo.write(f"{ii}\t{line.strip()}\n")

    # delete unnecessary files
    os.system(f"rm {outpath}_unnum.gdfa; rm {outpath}.fwd; rm {outpath}.rev; rm {outpath}.txt")
    return


def extract_alignments(corpusfile: list, vocab_size:int, i: int=-1):
    print(f"Extracting alignments, i={i}, vocab_size={vocab_size}\n")
    outpath = join(bpedir, mode, f"{vocab_size}{'_'+str(i) if i != -1 else ''}")

    create_parallel_text(corpusfile, vocab_size, i)
    create_fwd_rev_files(outpath)
    create_gdfa_file(outpath)
    return
