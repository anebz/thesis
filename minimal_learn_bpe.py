#!/usr/bin/env python
import os
import sys
import copy
import inspect
import codecs
from collections import defaultdict, Counter

def get_vocabulary(fobj):
    """Read text and return dictionary that encodes vocabulary
    """
    vocab = Counter()
    for line in fobj:
        _, line = line.split('\t')
        for word in line.strip('\r\n ').split(' '):
            if word:
                # split word into chars and add '</w>' at the end of the word
                word_splitted = tuple(word[:-1]) + (word[-1] + '</w>',)
                vocab[word_splitted] += 1
    return vocab


def get_pair_statistics(vocab):
    """Count frequency of all symbol pairs, and create index"""

    # data structure of pair frequencies
    stats = defaultdict(int)

    #index from pairs to words
    indices = defaultdict(lambda: defaultdict(int))

    for i, (word, freq) in enumerate(vocab):
        prev_char = word[0]
        for char in word[1:]:
            stats[prev_char, char] += freq # \U0001F917
            # dict of dict. first key is tuple of bigram, 
            # second key is the index where it's found, last value is the frequency
            # the only option where freq might be >1 is if the same bigram is repeated many times in the same index
            # which is highly unlikely
            indices[prev_char, char][i] += 1
            prev_char = char

    return stats, indices


def learn_bpe(infile, outfile, num_symbols, min_frequency=2, verbose=False, total_symbols=False):
    """Learn num_symbols BPE operations from vocabulary, and write to outfile.
    """
    # 1. split corpus into characters, count frequency
    vocab = get_vocabulary(infile)
    sorted_vocab = sorted(vocab.items(), key=lambda x: x[1], reverse=True)

    # 2. count bigrams in corpus
    stats, indices = get_pair_statistics(sorted_vocab)
    #big_stats = copy.deepcopy(stats)

if __name__ == '__main__':

    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    argsinput = codecs.open(os.path.join(currentdir, 'data/eng_with_10k.txt'), encoding='utf-8')
    argsoutput = codecs.open(os.path.join(currentdir, 'data/_out.txt'), 'w', encoding='utf-8')

    learn_bpe(argsinput, argsoutput, 100, min_frequency=2, verbose=True, total_symbols=10000)
