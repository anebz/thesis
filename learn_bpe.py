#!/usr/bin/env python

# inspired by https://gist.github.com/akashjaswal/ba302b943dfb4e56ace0d5761d01b9cf#file-bpe-py
import os
from os.path import join
import re
import sys
import glob
import inspect
import codecs
from collections import defaultdict, Counter
from tqdm import tqdm
from time import time


def build_vocab(corpus: list) -> dict:
    """
    Read corpus and return dictionary containing each word and its frequency in the corpus
    """

    tokens = []
    for line in corpus:
        line = line.split('\t')[1].strip('\r\n ').split(' ')
        for word in line:
            tokens.append(u'\u2581' + ' '.join(word))

    vocab = Counter(tokens)
    return vocab


def get_stats(vocab: dict) -> dict:
    """
    Count frequency of all symbol pairs
    """

    pairs = defaultdict(int)
    for word, freq in vocab.items():
        symbols = word.split()
        # Counting up occurrences of pairs
        for i in range(len(symbols) - 1):
            pairs[symbols[i], symbols[i + 1]] += freq

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


def learn_bpe(corpus, bpe_model, num_symbols):
    """
    Learn num_symbols BPE operations from vocabulary, and write to bpe_model.
    """
    # 1. split corpus into characters, count frequency
    vocab = build_vocab(corpus)

    stats_time = 0
    replace_time = 0

    for i in tqdm(range(num_symbols)):

        a = time()
        # 2. count bigrams in corpus
        pairs = get_stats(vocab)
        stats_time += time() - a

        if not pairs:
            break

        # 3. merge symbols
        most_frequent = max(pairs, key=pairs.get)
        a = time()
        vocab = replace_pair(most_frequent, vocab)
        replace_time += time() - a

        if i % 20 == 0:
            print(f"stats time {stats_time}, replace time {replace_time}")

        # 4. write merge list to file
        bpe_model.write('{0} {1}\n'.format(*most_frequent))
    return


if __name__ == '__main__':

    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    datapath = join(currentdir, 'data')

    num_symbols = 10000

    os.chdir(join(datapath, 'input'))
    for ifile in glob.glob("*.txt"):
        lang = ifile.split('_')[0]

        # check if a BPE model for this language exists
        # if so, only create new BPE model if num_symbols > symbols in the model
        model_path = join(datapath, lang+'.model')
        if os.path.isfile(model_path):
            bpe_model = codecs.open(model_path, encoding='utf-8').readlines()
            if bpe_model:
                model_symbols = bpe_model[0].strip('\r\n').split()[1]
                if num_symbols < int(model_symbols):
                    print(f"There already exists a model with at least {num_symbols} symbols")
                    sys.exit()
        
        argsinput = codecs.open(ifile, encoding='utf-8')
        bpe_model = codecs.open(model_path, 'w', encoding='utf-8')
        bpe_model.write('{0} {1}\n'.format(lang, num_symbols))

        print("Learning {} BPE symbols for {}".format(num_symbols, lang))
        learn_bpe(argsinput, bpe_model, num_symbols)
