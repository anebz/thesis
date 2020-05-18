import os
from os.path import join
import sys
import copy
import codecs
from tqdm import tqdm

# import global variables from lib/__init__.py
from lib import *

def merge_dropout_alignments():
    union_merge = {}
    inter_merge = {}
    #threshold_merge = {}

    os.chdir(join(bpedir, 'fastalign'))
    for num_symbols in all_symbols:
        for i in range(dropout_repetitions):
            alfile = str(num_symbols) + '_' + str(i) + '.wgdfa'
            for j, line in enumerate(open(alfile, 'r').readlines()):
                al = frozenset(line.strip().split("\t")[1].split())
                if i == 0:
                    if num_symbols not in union_merge:
                        union_merge[num_symbols] = [al]
                        inter_merge[num_symbols] = [al]
                        #threshold_merge[num_symbols] = [al]
                    else:
                        union_merge[num_symbols].append(al)
                        inter_merge[num_symbols].append(al)
                        #threshold_merge[num_symbols].append(al)
                    continue
                union_merge[num_symbols][j] |= al
                inter_merge[num_symbols][j] &= al

        unionfile = codecs.open(str(num_symbols)+'_union.wgdfa', 'w', encoding='utf-8')
        interfile = codecs.open(str(num_symbols)+'_inter.wgdfa', 'w', encoding='utf-8')

        for i in range(len(union_merge[num_symbols])):
            unionfile.write(f"{i}\t{' '.join(union_merge[num_symbols][i])}\n")
            interfile.write(f"{i}\t{' '.join(inter_merge[num_symbols][i])}\n")
    return


if __name__ == "__main__":
    merge_dropout_alignments()

