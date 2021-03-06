#!/usr/bin/env python3
import os
import sys
import json
import codecs
import random
from tqdm import tqdm
from os.path import join

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from settings import *
from learn_bpe import read_corpus, join_best_mappings

def write_bpe(lang: str, vocab_size: int, str_corpus: str, i: int=-1):
    outputpath = join(bpedir, 'segmentations', f"{lang}_{vocab_size}{'_'+str(i) if params[lang]['dropout'] else ''}.bpe")
    codecs.open(outputpath, 'w', encoding='utf-8').write(str_corpus)


def apply_bpe(lang: str, bpe_model: list, corpus: str, i: int=-1):
    str_corpus = '\n'.join(corpus)
    for j, bigram in enumerate(bpe_model[:merges[-1]]):

        if j+1 in merges:
            write_bpe(lang, j+1, str_corpus, i)

        if random.uniform(0, 1) < params[lang]['dropout']:
            continue

        str_corpus = str_corpus.replace(' '.join(bigram), ''.join(bigram))
    return str_corpus


def apply_bpe_fancy(lang: str, bpe_model: list, corpus: str, vocab_size: int, i: int=-1):

    corpus = join_best_mappings(lang, corpus, vocab_size)
    str_corpus = '\n'.join(corpus)
    for j, bigram in enumerate(bpe_model[:vocab_size]):

        if random.uniform(0, 1) < params[lang]['dropout']:
            continue

        str_corpus = str_corpus.replace(' '.join(bigram), ''.join(bigram))
    write_bpe(lang, j+1, str_corpus, i)
    return
