# global variables
import os
from os.path import join
import sys

word_sep = u'\u2581'
source, target = 'eng', 'deu' #eng, deu
source_bpe, target_bpe = False, False # both can't be true at the same time

dropout = 0.3 # 0
dropout_repetitions = 10
merge_threshold = [0.3, 0.5, 0.7, 0.9] # if alignments are present in >X% of files, they're accepted
avgs = [3, 5, 7, 10] # average dropout scores, avg of 3, 5, ...

rootdir = os.getcwd()
if rootdir.split(os.sep)[-1] == 'src':
    rootdir = os.sep.join(rootdir.split(os.sep)[:-1])
datadir = join(rootdir, 'data')
inputdir = join(datadir, 'input')
bpedir = join(datadir, 'dropout_bpe' if dropout > 0 else 'normal_bpe')
scoredir = join(rootdir, 'reports', 'scores_' + ('dropout_bpe' if dropout > 0 else 'normal_bpe'))
goldpath = join(inputdir, 'eng_deu.gold')
inputpath = {source: join(inputdir, source+'_with_10k.txt'),
            target: join(inputdir, target+'_with_10k.txt')}

fastalign_path = join(rootdir, "tools/fast_align/build/fast_align")
atools_path = join(rootdir, "tools/fast_align/build/atools")

space = False
num_all_symbols = 10000 #10000
all_symbols = [100, 200, 500, 1000, 2000, 4000]
