# global variables
import os
import sys
from os.path import join

word_sep = u'\u2581' # symbol to use for word separators
source, target = 'eng', 'deu' # eng, deu, ron, hin
mode = "fastalign"  # fastalign, eflomal
it = 0
max_it = 4

params = {
    source: {
        'bpe': False,
        'space': True,
        'dropout': 0
    },
    target: {
        'bpe': True,
        'space': False,
        'dropout': 0.2
    }
}

learn_vocab_size = 8000  # how many BPE units to learn in learn_bpe.py
merges = [100, 200, 500, 1000, 2000, 4000] # vocabulary size for segmentations
dropout_samples = 10 # how many samples to create in dropout mode
merge_threshold = [0.5] # alignment threshold for dropout mode

# paths for input files
rootdir = os.getcwd()
if rootdir.split(os.sep)[-1] == 'src':
    rootdir = os.sep.join(rootdir.split(os.sep)[:-1])
inputdir = join(rootdir, 'data', 'input', source+'-'+target)

#! Check input corpus before running pipeline
inputpath = {}
inputpath[source] = join(inputdir, source+'_with_10k.txt')
inputpath[target] = join(inputdir, target+'_with_10k.txt')

# paths for intermediate files
baselinedir = join(rootdir, 'reports', 'scores_normal_bpe')
bpedir = join(rootdir, 'data', 'dropout_bpe' if params[target]['dropout'] else 'normal_bpe')
scoredir = join(rootdir, 'reports', 'scores_' + ('dropout_bpe' if params[target]['dropout'] else 'normal_bpe'),
                'space' if params[target]['space'] else 'no space', )

os.makedirs(join(bpedir, 'segmentations'), exist_ok=True)
os.makedirs(join(bpedir, 'fastalign'), exist_ok=True)

# paths for alignment algorithms
fastalign_path = join(rootdir, "tools/fast_align/build/fast_align")
atools_path = join(rootdir, "tools/fast_align/build/atools")
eflomal_path = join(rootdir, "tools/eflomal")
