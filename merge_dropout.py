import os
from os.path import join
import sys
import copy
import codecs
from tqdm import tqdm
from collections import Counter

# import global variables from lib/__init__.py
from lib import *

def merge_dropout_alignments():
    union_merge, inter_merge, thres_merge = {}, {}, {}

    os.chdir(join(bpedir, 'fastalign'))
    for num_symbols in tqdm(all_symbols):
        union_merge[num_symbols], inter_merge[num_symbols], thres_merge[num_symbols] = [], [], []

        for i in range(dropout_repetitions):

            for j, line in enumerate(open(str(num_symbols)+'_'+str(i)+'.wgdfa', 'r').readlines()):
                al = frozenset(line.strip().split("\t")[1].split())

                # at the first iteration, just append the alignment
                if i == 0:
                    union_merge[num_symbols].append(al)
                    inter_merge[num_symbols].append(al)
                    thres_merge[num_symbols].append(Counter(al))
                    continue
                
                # do union, intersection or frequency addition
                union_merge[num_symbols][j] |= al
                inter_merge[num_symbols][j] &= al
                thres_merge[num_symbols][j] += Counter(al)

        # write to output
        unionfile = codecs.open(str(num_symbols)+'_union.wgdfa', 'w')
        interfile = codecs.open(str(num_symbols)+'_inter.wgdfa', 'w')
        thresfile = codecs.open(str(num_symbols)+'_thres.wgdfa', 'w')

        for i in range(len(union_merge[num_symbols])):
            unionfile.write(f"{i}\t{' '.join(union_merge[num_symbols][i])}\n")
            interfile.write(f"{i}\t{' '.join(inter_merge[num_symbols][i])}\n")

            # get alignments more common than the merge_threshold % 
            common_aligns = [k for k in thres_merge[num_symbols][i] 
                             if thres_merge[num_symbols][i][k] > merge_threshold * dropout_repetitions]
            thresfile.write(f"{i}\t{' '.join(common_aligns)}\n")
    return


if __name__ == "__main__":
    print("Merging dropouts")
    merge_dropout_alignments()

    for merge_type in ['union', 'inter', 'thres']:
        pass
