#!/usr/bin/env python3
import os
import sys
import json
import codecs
import random
from tqdm import tqdm
from os.path import join

# import global variables from settings.py
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from settings import *
from learn_bpe import read_bpe_model, read_corpus


def load_data(lang: str) -> (list, list):

    argsinput = codecs.open(inputpath[lang], encoding='utf-8')
    corpus = read_corpus(lang, argsinput)

    bpe_model, _ = read_bpe_model(lang)
    if not bpe_model:
        print(f"No model found for lang={lang}")
        sys.exit()
    bpe_model = [tuple(item.strip('\r\n ').split()) for n, item in enumerate(bpe_model)]
    
    return bpe_model[1:], corpus


def write_bpe(lang: str, num_symbols: int, str_corpus: str, i: int=-1):
    outputpath = join(bpedir, 'segmentations', f"{lang}_{num_symbols}{'_'+str(i) if i != -1 else ''}.bpe")
    codecs.open(outputpath, 'w', encoding='utf-8').write(str_corpus)


def apply_bpe(lang: str, bpe_model: list, corpus: str, i: int=-1):
    str_corpus = '\n'.join(corpus)
    for j, bigram in enumerate(tqdm(bpe_model[:merges[-1]], desc=f"apply_bpe: lang={lang}, it={i}")):

        if j+1 in merges:
            write_bpe(lang, j+1, str_corpus, i)

        if random.uniform(0, 1) < params[lang]['dropout']:
            continue

        str_corpus = str_corpus.replace(' '.join(bigram), ''.join(bigram))
    return


if __name__ == "__main__":
    os.makedirs(join(bpedir, 'segmentations'), exist_ok=True)
    
    for lang in [source, target]:

        if not params[lang]['bpe']:
            continue
        bpe_model, corpus = load_data(lang)
        print(f"{lang} parameters: {json.dumps(params[lang], indent=2)}")
        if params[lang]['dropout']:
            for i in range(dropout_samples):
                apply_bpe(lang, bpe_model, corpus, i)
        else:
            apply_bpe(lang, bpe_model, corpus)
