#!/usr/bin/env python

# inspired by https://gist.github.com/akashjaswal/ba302b943dfb4e56ace0d5761d01b9cf#file-bpe-py
import os
from os.path import join
import re
import sys
import codecs
from collections import defaultdict, Counter
from tqdm import tqdm
from time import time

# import global variables from lib/__init__.py
from lib import *


def build_vocab(corpus):
    """
    Read corpus and return dictionary containing each word and its frequency in the corpus.
    Words are separated by spaces.
    Each word has a u'\u2581' symbol at the beginning to signal it's the beginning of the word.
    """

    tokens = []
    for line in corpus:
        line = line.split('\t')[1].strip('\r\n ').split(' ')
        for word in line:
            tokens.append(u'\u2581' + ' '.join(word))

    vocab = Counter(tokens)
    return vocab


def build_vocab_no_space(corpus: list) -> dict:
    """
    Read corpus and return dictionary containing each word and its frequency in the corpus.
    In no_space mode, space is replaced by u'\u2581' and considered as a token.
    The u'\u2581' symbol in the beginning of each word is no longer used.
    """

    vocab = ''
    for line in corpus:
        line = line.split('\t')[1].strip('\r\n').replace(' ', u'\u2581')
        vocab += line.replace('', ' ') + '\n'

    return vocab


def get_stats(vocab: dict) -> dict:
    """
    Count frequency of all symbol pairs
    """

    pairs = Counter()
    for word, freq in vocab.items():
        symbols = word.split()
        # Counting up occurrences of pairs
        for i in range(len(symbols) - 1):
            pairs[symbols[i], symbols[i + 1]] += freq

    return pairs


def get_stats_no_space(vocab):
    """
    Count frequency of all symbol pairs.
    range(2) for bigrams
    """

    pairs = Counter()
    for sent in vocab.split('\n'):
        words = sent.split()
        pairs += Counter(zip(*[words[i:] for i in range(2)]))

    return pairs


def replace_pair(pair: tuple, vocab: dict) -> dict:
    """
    Replace all occurrences of a symbol pair ('A', 'B') with a new symbol 'AB'
    """
    merged_vocab = defaultdict(str)
    bigram = re.escape(' '.join(pair))
    p = re.compile(r'(?<!\S)' + bigram + r'(?!\S)')

    for word in vocab:
        # replace most frequent pair in all vocabulary
        merged_word = p.sub(''.join(pair), word)
        merged_vocab[merged_word] = vocab[word]

    return merged_vocab



def replace_pair_no_space(pair: tuple, vocab: list) -> dict:
    """
    Replace all occurrences of a symbol pair ('A', 'B') with a new symbol 'AB'
    """
    bigram = re.escape(' '.join(pair))
    p = re.compile(r'(?<!\S)' + bigram + r'(?!\S)')

    return p.sub(''.join(pair), vocab)


def learn_bpe(corpus, bpe_model, num_symbols):
    """
    Learn num_symbols BPE operations from vocabulary, and write to bpe_model.
    """
    # 1. split corpus into characters, count frequency
    vocab = build_vocab(corpus) if space else build_vocab_no_space(corpus)

    for i in tqdm(range(num_symbols)):

        # 2. count bigrams in corpus
        pairs = get_stats(vocab) if space else get_stats_no_space(vocab)

        if not pairs:
            break

        # 3. merge symbols
        most_frequent = pairs.most_common(1)[0][0]
        vocab = replace_pair(most_frequent, vocab) if space else replace_pair_no_space(most_frequent, vocab)

        # 4. write merge list to file
        bpe_model.write('{0} {1}\n'.format(*most_frequent))
    return


if __name__ == '__main__':

    for lang in [source, target]:

        # check if a BPE model for this language exists
        # if so, only create new BPE model if num_symbols > symbols in the model
        model_path = join(datadir, lang+('' if space else '_ns')+'.model')
        if os.path.isfile(model_path):
            bpe_model = codecs.open(model_path, encoding='utf-8').readlines()
            if bpe_model:
                model_symbols = bpe_model[0].strip('\r\n').split()[1]
                if num_symbols < int(model_symbols):
                    print(f"There already exists a model with at least {num_symbols} symbols")
                    sys.exit()
        
        argsinput = codecs.open(inputpath[lang], encoding='utf-8')
        bpe_model = codecs.open(model_path, 'w', encoding='utf-8')
        bpe_model.write('{0} {1}\n'.format(lang, num_symbols))

        print(f"Learning {num_symbols} BPE symbols for lang={lang}, space mode={space}")
        learn_bpe(argsinput, bpe_model, num_symbols)
