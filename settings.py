# global variables
import os
import sys
from os.path import join

word_sep = u'\u2581' # symbol to use for word separators
source, target = 'eng', 'deu' # eng, deu, ron, hin
mode = "fastalign"  # fastalign, eflomal
scoring = False # True to activate the scoring method
it = 0
threshold = 0.1

params = {
    source: {
        'bpe': False,
        'space': True,
        'dropout': 0
    },
    target: {
        'bpe': True,
        'space': False,
        'dropout': 0.3
    }
}

learn_merges = 10000 # how many BPE units to learn in learn_bpe.py
merges = [8000] # create segmentations with different number of merges
dropout_samples = 10 # how many samples to create in dropout mode
merge_threshold = [0.5, 0.7] # alignment threshold for dropout mode

# paths for input files
rootdir = os.getcwd()
if rootdir.split(os.sep)[-1] == 'src':
    rootdir = os.sep.join(rootdir.split(os.sep)[:-1])
inputdir = join(rootdir, 'data', 'input', source+'-'+target)

inputpath = {}
inputpath[source] = join(inputdir, 'train.'+source)
inputpath[target] = join(inputdir, 'train.'+target)

# paths for intermediate files
baselinedir = join(rootdir, 'reports', 'scores_normal_bpe')
bpedir = join(rootdir, 'data', 'dropout_bpe' 
            if max(params[source]['dropout'], params[target]['dropout']) else 'normal_bpe')
scoredir = join(rootdir, 'reports', 'scores_' + ('dropout_bpe' 
            if max(params[source]['dropout'], params[target]['dropout']) else 'normal_bpe'))

# paths for alignment algorithms
fastalign_path = join(rootdir, "tools/fast_align/build/fast_align")
atools_path = join(rootdir, "tools/fast_align/build/atools")
eflomal_path = join(rootdir, "tools/eflomal")
