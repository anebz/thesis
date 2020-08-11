import os
from os.path import join
import sys
import codecs
import random
from tqdm import tqdm

# import global variables from settings.py
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from settings import *
from learn_bpe import read_bpe_model, read_corpus


def load_data() -> (list, list, list):

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


def write_bpe(lang: str, num_symbols: int, str_corpus: str, i: int =-1):
    outputpath = join(bpedir, 'segmentations',
                      f"{lang}_{num_symbols}{'' if space else '_ns'}{'_'+str(i) if i != -1 else ''}.bpe")
    codecs.open(outputpath, 'w', encoding='utf-8').write(str_corpus)


def apply_bpe(langs: list, bpe_models: list, corpora: list, i: int =-1):
    
    for lang, bpe_model, corpus in zip(langs, bpe_models, corpora):

        str_corpus = '\n'.join(corpus)
        for j, bigram in enumerate(tqdm(bpe_model[:merges[-1]], desc=f"apply_bpe: dropout={dropout}, lang={lang}")):

            if j+1 in merges:
                write_bpe(lang, j+1, str_corpus, i)

            if random.uniform(0, 1) < dropout:
                continue

            str_corpus = str_corpus.replace(' '.join(bigram), ''.join(bigram))
    return


if __name__ == "__main__":

    langs, bpe_models, corpora = load_data()

    os.makedirs(join(bpedir, 'segmentations'), exist_ok=True)
    if dropout > 0:
        # create `dropout_samples` segmentations, to aggregate later
        for i in range(dropout_samples):
            print(f"Iteration {i+1}")
            apply_bpe(langs, bpe_models, corpora, i)
    else:
        apply_bpe(langs, bpe_models, corpora)
