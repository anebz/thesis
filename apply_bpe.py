import os
from os.path import join
import codecs
import random
from tqdm import tqdm

# import global variables from settings.py
from settings import *
from learn_bpe import read_bpe_model, read_corpus


def load_data():

    os.chdir(datadir)
    langs = [source, target]
    bpe_models = []
    corpora = []
    for lang in langs:

        argsinput = codecs.open(inputpath[lang], encoding='utf-8')
        corpora.append(read_corpus(argsinput))

        bpe_model, _ = read_bpe_model(lang)
        if not bpe_model:
            print(f"No model found for lang={lang}")

        bpe_model = [tuple(item.strip('\r\n ').split(' ')) for (n, item) in enumerate(bpe_model)]
        bpe_models.append(bpe_model[1:])

    return langs, bpe_models, corpora


def merge_corpus(corpus, bpe_model, lang, num_symbols):
    '''
    merge the bigrams found in the corpus iteratively
    Inputs: 
    * corpus in the style from read_corpus
    * bpe_model read from the input file
    Output:
    * Merged corpus
    '''

    str_corpus = '\n'.join(corpus)
    for bigram in tqdm(bpe_model, desc=f"apply_bpe: lang={lang}, num_symbols={num_symbols}, dropout={dropout*100}%"):

        if random.uniform(0, 1) < dropout:
            continue

        str_corpus = str_corpus.replace(' '.join(bigram), ''.join(bigram))
    
    return str_corpus


def apply_bpe(i=-1):
    os.chdir(datadir)
    for num_symbols in all_symbols:
        for lang, bpe_model, corpus in zip(langs, bpe_models, corpora):

            # only get the desired amount of symbols
            bpe_model = bpe_model[:num_symbols]

            merged_corpus = merge_corpus(corpus, bpe_model, lang, num_symbols)

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
    else:
        apply_bpe()
