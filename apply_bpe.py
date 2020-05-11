import os
from os.path import join
import sys
import glob
import codecs
import random
from tqdm import tqdm

# import global variables from lib/__init__.py
from lib import *

def load_data():

    os.chdir(datadir)
    langs = []
    bpe_models = []
    corpora = []
    for ifile in glob.glob("*.model"):

        lang = ifile.split('.')[0]
        langs.append(lang)

        bpe_model = codecs.open(ifile, encoding='utf-8').readlines()

        model_symbols = bpe_model[0].strip('\r\n').split()[1]
        if max(all_symbols) > int(model_symbols):
            print(f"Asking for {max(all_symbols)} but the BPE model only has {model_symbols}")
            sys.exit()

        bpe_model = [tuple(item.strip('\r\n ').split(' ')) for (n, item) in enumerate(bpe_model)]
        bpe_models.append(bpe_model)

        argsinput = codecs.open(join(datadir, 'input/'+lang+'_with_10k.txt'), encoding='utf-8')
        corpora.append(read_corpus(argsinput))

    return langs, bpe_models, corpora


def read_corpus(argsinput):
    '''
    read corpus into list of list of bigram tuples
    Input: argsinput
        [
            '1   This is the first line',
            '2   The second line',
            ....
        ]
    Output:
        [
            '_W', 'e',
            '_d', 'o',
            '_n', 'o', 't',
            '_b', 'e', 'l', 'i', 'e', 'v', 'e',
            ...
            '\n',
            ...
        ]
    '''

    corpus = []
    for line in argsinput:
        # line.split('\t')[1] to strip the number in the line
        line = line.split('\t')[1].strip('\r\n ').split(' ')
        for word in line:
            # add '_' to beginning of each word
            newword = [u'\u2581' + word[0]]
            newword.extend(list(word[1:]))
            corpus.extend(newword)
        corpus.append('\n')
    return corpus


def merge_corpus(corpus, bpe_merges, dropout=0.1):
    '''
    merge the bigrams found in the corpus iteratively
    Inputs: 
    * corpus in the style from read_corpus
    * bpe_merges read from the input file
    Output:
    * Merged corpus
    '''

    str_corpus = ' '.join(corpus)
    for bigram in tqdm(bpe_merges):

        if random.uniform(0, 1) < dropout:
            continue
        # merge bigram
        str_corpus = str_corpus.replace(' '.join(bigram), ''.join(bigram))
    
    return str_corpus.replace(' \n ', '\n')


def apply_bpe(i=-1):
    os.chdir(datadir)
    for num_symbols in all_symbols:
        for lang, bpe_model, corpus in zip(langs, bpe_models, corpora):

            # only get the desired amount of symbols
            bpe_model = bpe_model[1:num_symbols+1]

            print(f"Merging BPE symbols for {lang}, {num_symbols} symbols and dropout {dropout*100}%")

            merged_corpus = merge_corpus(corpus, bpe_model, dropout)

            outputpath = join(bpedir, 'segmentations', lang+"_"+str(num_symbols)+('_'+str(i) if i != -1 else '')+".bpe")
            argsoutput = codecs.open(outputpath, 'w', encoding='utf-8')
            argsoutput.write(merged_corpus)
    return


if __name__ == "__main__":

    langs, bpe_models, corpora = load_data()

    if dropout > 0:
        # create `dropout_repetitions` segmentations, to aggregate later
        for i in range(dropout_repetitions):
            print(f"Iteration {i+1}")
            apply_bpe(i)
            print("\n\n\n\n")
    else:
        apply_bpe()
