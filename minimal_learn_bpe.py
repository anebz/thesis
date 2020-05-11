#!/usr/bin/env python
import os
from os.path import join
import re
import sys
import copy
import glob
import inspect
import codecs
from collections import defaultdict, Counter
from tqdm import tqdm

def get_vocabulary(fobj):
    """
    word vocabulary
    Read text and return dictionary that encodes vocabulary
    """
    vocab = Counter()
    for line in fobj:
        line = line.split('\t')[1].strip('\r\n ').split(' ')
        for word in line:
            # split word into chars, while adding ▁ to the first word
            word_splitted = (u'\u2581' + word[0],) + tuple(word[1:])
            vocab[word_splitted] += 1
    return vocab


def get_pair_statistics(vocab):
    """
    Count frequency of all symbol pairs, and create index
    """

    # data structure of pair frequencies
    stats = defaultdict(int)

    #index from pairs to words
    indices = defaultdict(lambda: defaultdict(int))

    for i, (word, freq) in enumerate(vocab):
        prev_char = word[0]
        for char in word[1:]:
            stats[prev_char, char] += freq
            # dict of dict. first key is tuple of bigram, 
            # second key is the index where it's found, last value is the frequency
            # the only option where freq might be >1 is if the same bigram is repeated many times in the same index
            # which is highly unlikely
            indices[prev_char, char][i] += 1
            prev_char = char

    return stats, indices


def replace_pair(pair, vocab, indices):
    """
    Replace all occurrences of a symbol pair ('A', 'B') with a new symbol 'AB'
    """
    first, second = pair
    pair_str = ''.join(pair)
    pair_str = pair_str.replace('\\', '\\\\')
    changes = []
    pattern = re.compile(r'(?<!\S)' + re.escape(first + ' ' + second) + r'(?!\S)')
    iterator = indices[pair].items()
    
    # do this for all occurrences of the pair in the corpus
    for i, freq in iterator:
        word, freq = vocab[i]
        # split into chars
        new_word = ' '.join(word)
        # merge
        new_word = pattern.sub(pair_str, new_word)
        # join again
        new_word = tuple(new_word.split(' '))

        vocab[i] = (new_word, freq)
        changes.append((i, new_word, word, freq))

    return changes

# TODO understand this better
def update_pair_statistics(pair, changed, stats, indices):
    """
    Minimally update the indices and frequency of symbol pairs

    if we merge a pair of symbols, only pairs that overlap with occurrences
    of this pair are affected, and need to be updated.
    """
    stats[pair] = 0
    indices[pair] = defaultdict(int)
    first, second = pair
    new_pair = first+second
    for j, word, old_word, freq in changed:

        # find all instances of pair, and update frequency/indices around it
        i = 0
        while True:
            # find first symbol
            try:
                i = old_word.index(first, i)
            except ValueError:
                break
            # if first symbol is followed by second symbol, we've found an occurrence of pair (old_word[i:i+2])
            if i < len(old_word)-1 and old_word[i+1] == second:
                # assuming a symbol sequence "A B C", if "B C" is merged, reduce the frequency of "A B"
                if i:
                    prev = old_word[i-1:i+1]
                    stats[prev] -= freq
                    indices[prev][j] -= 1
                if i < len(old_word)-2:
                    # assuming a symbol sequence "A B C B", if "B C" is merged, reduce the frequency of "C B".
                    # however, skip this if the sequence is A B C B C, because the frequency of "C B" will be reduced by the previous code block
                    if old_word[i+2] != first or i >= len(old_word)-3 or old_word[i+3] != second:
                        nex = old_word[i+1:i+3]
                        stats[nex] -= freq
                        indices[nex][j] -= 1
                i += 2
            else:
                i += 1

        i = 0
        while True:
            try:
                # find new pair
                i = word.index(new_pair, i)
            except ValueError:
                break
            # assuming a symbol sequence "A BC D", if "B C" is merged, increase the frequency of "A BC"
            if i:
                prev = word[i-1:i+1]
                stats[prev] += freq
                indices[prev][j] += 1
            # assuming a symbol sequence "A BC B", if "B C" is merged, increase the frequency of "BC B"
            # however, if the sequence is A BC BC, skip this step because the count of "BC BC" will be incremented by the previous code block
            if i < len(word)-1 and word[i+1] != new_pair:
                nex = word[i:i+2]
                stats[nex] += freq
                indices[nex][j] += 1
            i += 1
    return

def learn_bpe(infile, outfile, num_symbols):
    """
    Learn num_symbols BPE operations from vocabulary, and write to outfile.
    """
    # 1. split corpus into characters, count frequency
    vocab = get_vocabulary(infile)
    # why sort it?
    sorted_vocab = sorted(vocab.items(), key=lambda x: x[1], reverse=True)

    # 2. count bigrams in corpus
    stats, indices = get_pair_statistics(sorted_vocab)
    #big_stats = copy.deepcopy(stats)

    # 3. merge symbols
    for _ in tqdm(range(num_symbols)):
        if stats:
            most_frequent = max(stats, key=lambda x: (stats[x], x))

        changes = replace_pair(most_frequent, sorted_vocab, indices)
        update_pair_statistics(most_frequent, changes, stats, indices)
        stats[most_frequent] = 0

        # 4. write merge list to file
        outfile.write('{0} {1}\n'.format(*most_frequent))
    return

if __name__ == '__main__':

    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    datadir = join(currentdir, 'data')

    num_symbols = 10000

    os.chdir(join(datadir, 'input'))
    for ifile in glob.glob("*.txt"):
        lang = ifile.split('_')[0]

        # check if a BPE model for this language exists
        # if so, only create new BPE model if num_symbols > symbols in the model
        model_path = join(datadir, lang+'.model')
        if os.path.isfile(model_path):
            bpe_model = codecs.open(model_path, encoding='utf-8').readlines()
            model_symbols = bpe_model[0].strip('\r\n').split()[1]
            if num_symbols < int(model_symbols):
                print(f"There already exists a model with at least {num_symbols} symbols")
                sys.exit()
        
        argsinput = codecs.open(ifile, encoding='utf-8')
        argsoutput = codecs.open(model_path, 'w', encoding='utf-8')
        argsoutput.write('{0} {1}\n'.format(lang, num_symbols))

        print("Learning {} BPE symbols for {}".format(num_symbols, lang))
        learn_bpe(argsinput, argsoutput, num_symbols)
