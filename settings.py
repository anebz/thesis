# global variables
import os
from os.path import join
import sys

source, target = 'eng', 'deu' #eng, deu
source_bpe, target_bpe = False, False # both can't be true at the same time

dropout = 0.1 # 0
dropout_repetitions = 30
merge_threshold = 0.9 # 0.3, 0.5, 0.7, 0.9 # if alignments are present in >X% of files, they're accepted
avgs = [3, 5, 7, 10] # average dropout scores, avg of 3, 5, ...

rootdir = os.getcwd()
datadir = join(rootdir, 'data')
bpedir = join(datadir, 'dropout_bpe' if dropout > 0 else 'normal_bpe')
goldpath = join(datadir, 'input', 'eng_deu.gold')
inputpath = {source: join(datadir, 'input', source+'_with_10k.txt'),
            target: join(datadir, 'input', target+'_with_10k.txt')}

fastalign_path = join(rootdir, "tools/fast_align/build/fast_align")
atools_path = join(rootdir, "tools/fast_align/build/atools")

space = True
num_symbols = 10000 #10000
all_symbols = [2000, 4000]#[100, 500, 1000, 2000, 4000, 8000]
