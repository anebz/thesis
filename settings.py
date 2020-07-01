# global variables
import os
from os.path import join
import sys

word_sep = u'\u2581'
source, target = 'eng', 'deu' #eng, deu
source_bpe, target_bpe = False, False # both can't be true at the same time

space = True
dropout = 0
dropout_samples = 10
num_all_symbols = 20000
all_symbols = [100, 200, 500, 1000, 2000, 4000, 6000, 8000]
merge_threshold = [0.3, 0.5, 0.7, 0.9] # if alignments are present in >X% of files, they're accepted
#avgs = [3, 5, 7, 10] # average dropout scores, avg of 3, 5, ...

rootdir = os.getcwd()
if rootdir.split(os.sep)[-1] == 'src':
    rootdir = os.sep.join(rootdir.split(os.sep)[:-1])
datadir = join(rootdir, 'data')
inputdir = join(datadir, 'input', source+'-'+target)
bpedir = join(datadir, 'dropout_bpe' if dropout > 0 else 'normal_bpe')
baselinedir = join(rootdir, 'reports', 'scores_normal_bpe')
scoredir = join(rootdir, 'reports', 'scores_' + ('dropout_bpe' if dropout > 0 else 'normal_bpe'))
goldpath = join(inputdir, source+'_'+target+'.gold')
inputpath = {source: join(inputdir, source+'_with_10k.txt'),
            target: join(inputdir, target+'_with_10k.txt')}

mode = "eflomal" #fastalign
fastalign_path = join(rootdir, "tools/fast_align/build/fast_align")
# https://github.com/robertostling/eflomal
eflomal_path = join(rootdir, "tools/eflomal")
atools_path = join(rootdir, "tools/fast_align/build/atools")
