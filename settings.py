# global variables
import os
import sys
import glob
from os.path import join

word_sep = u'\u2581'
source, target = 'eng', 'hin' #eng, deu, ron, hin
source_bpe, target_bpe = False, False # both can't be true at the same time

space = True
dropout = 0.1
dropout_samples = 10
learn_symbols = 10000
all_symbols = [1000]
merge_threshold = [0.7]

rootdir = os.getcwd()
if rootdir.split(os.sep)[-1] == 'src':
    rootdir = os.sep.join(rootdir.split(os.sep)[:-1])
datadir = join(rootdir, 'data')
inputdir = join(datadir, 'input', source+'-'+target)
bpedir = join(datadir, 'dropout_bpe' if dropout > 0 else 'normal_bpe')
baselinedir = join(rootdir, 'reports', 'scores_normal_bpe')
scoredir = join(rootdir, 'reports', 'scores_' + ('dropout_bpe' if dropout > 0 else 'normal_bpe'))
goldpath = join(inputdir, source+'_'+target+'.gold')

inputpath = {}
for filename in glob.glob(join(inputdir, "*.txt")):
    inputpath[filename.split(os.sep)[-1].split('_')[0]] = filename

mode = "fastalign" #fastalign, eflomal
fastalign_path = join(rootdir, "tools/fast_align/build/fast_align")
atools_path = join(rootdir, "tools/fast_align/build/atools")
eflomal_path = join(rootdir, "tools/eflomal")
