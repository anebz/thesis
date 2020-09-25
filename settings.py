# global variables
import os
import glob
from os.path import join

word_sep = u'\u2581' # symbol to use for word separators
source, target = 'eng', 'deu' # eng, deu, ron, hin
mode = "fastalign"  # fastalign, eflomal
source_bpe, target_bpe = False, True # Set True to source to make BPE only on source mode, same in Target. both can't be true at the same time

space = False # True for space mode, False for no space mode
scoring = False # True to activate the scoring method
dropout = 0.1 # dropout rate

learn_merges = 10000 # how many BPE units to learn in learn_bpe.py
merges = [200, 500] # create segmentations with different number of merges
dropout_samples = 10 # how many samples to create in dropout mode
merge_threshold = [0.5, 0.7] # alignment threshold for dropout mode

# paths for input files
rootdir = os.getcwd()
if rootdir.split(os.sep)[-1] == 'src':
    rootdir = os.sep.join(rootdir.split(os.sep)[:-1])
inputdir = join(rootdir, 'data', 'input', source+'-'+target)
goldpath = join(inputdir, source+'_'+target+'.gold')
inputpath = {}
for filename in glob.glob(join(inputdir, "*.txt")):
    inputpath[filename.split(os.sep)[-1].split('_')[0]] = filename

# paths for intermediate files
bpedir = join(rootdir, 'data', 'dropout_bpe' if dropout > 0 else 'normal_bpe')
baselinedir = join(rootdir, 'reports', 'scores_normal_bpe')
scoredir = join(rootdir, 'reports', 'scores_' + ('dropout_bpe' if dropout > 0 else 'normal_bpe'))

# paths for alignment algorithms
fastalign_path = join(rootdir, "tools/fast_align/build/fast_align")
atools_path = join(rootdir, "tools/fast_align/build/atools")
eflomal_path = join(rootdir, "tools/eflomal")
