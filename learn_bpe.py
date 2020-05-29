#!/usr/bin/env python

# inspired by https://gist.github.com/akashjaswal/ba302b943dfb4e56ace0d5761d01b9cf#file-bpe-py
import os
from os.path import join
import re
import sys
import codecs
from operator import itemgetter
from collections import defaultdict, Counter
from tqdm import tqdm

# import global variables from lib/__init__.py
from lib import *


def build_vocab(corpus):
    """
    Read corpus and return dictionary containing each word and its frequency in the corpus.
    Words are separated by spaces.
    Each word has a u'\u2581' symbol at the beginning to signal it's the beginning of the word.
    """

    vocab = Counter()
    for line in corpus:
        line = line.split('\t')[1].strip('\r\n ').replace('.', ' .').split()
        
        for word in line:
            vocab[u'\u2581' + ' '.join(word)] += 1

    return vocab


def build_vocab_no_space(corpus):
    """
    Read corpus and return dictionary containing each word and its frequency in the corpus.
    Words are separated by spaces.
    Each word has a u'\u2581' symbol at the beginning to signal it's the beginning of the word.
    """

    tokens = []
    for line in corpus:
        line = line.split('\t')[1].strip('\r\n ').replace('.', ' .').split()
        tokens.append(u' \u2581 '.join([' '.join(word) for word in line]))

    return tokens


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


def get_stats_no_space(tokens):
    """
    Count frequency of all symbol pairs.
    range(2) for bigrams
    """

    pairs = Counter()
    idx = defaultdict(set)
    for i, sent in enumerate(tokens):
        words = sent.split()
        for j in range(len(words) - 1):
            new_pair = words[j], words[j + 1]
            pairs[new_pair] += 1
            idx[new_pair].add(i)

    return pairs, idx


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


def update_tokens(tokens, idx, pairs, pair):

    bigram = ' '.join(pair)
    merged_bigram = ''.join(pair)
    lenb = len(merged_bigram) + 1

    tokens_to_visit = itemgetter(*list(idx[pair]))(tokens)
    for i, sent in enumerate(tokens_to_visit):

        for j in range(len(sent[:-lenb])):

            if sent[j:j+lenb] != bigram:
                continue
            
            if j != 0:
                # update previous token in pairs
                prev = (sent[:j].split()[-1], pair[0])
                pairs[prev] -= 1
                if pairs[prev] == 0:
                    del pairs[prev]
                
                new_bgm = (prev[0], merged_bigram)
                pairs[new_bgm] += 1
                idx[new_bgm].add(i)


            if j != len(sent):
                # update after token in pairs
                after = (pair[1], sent[j+lenb:].split()[0])
                pairs[after] -= 1
                if pairs[after] == 0:
                    del pairs[after]
                
                new_bgm = (merged_bigram, after[1])
                pairs[new_bgm] += 1
                idx[new_bgm].add(i)

    # delete bigram from pairs and idx
    del pairs[pair]
    del idx[pair]

    return tokens, idx, pairs



def learn_bpe(corpus, bpe_model, num_symbols):
    """
    Learn num_symbols BPE operations from vocabulary, and write to bpe_model.
    """
    # 1. split corpus into characters, count frequency
    #vocab = build_vocab(corpus) if space else build_vocab_no_space(corpus)
    tokens = build_vocab_no_space(corpus)

    # 2. count bigrams in corpus
    pairs, idx = get_stats_no_space(tokens)

    for i in tqdm(range(num_symbols)):

        # 2. count bigrams in corpus
        #pairs = get_stats(vocab) if space else get_stats_no_space(vocab)

        if not pairs:
            break

        # 3. merge symbols
        most_frequent = pairs.most_common(1)[0][0]
        #vocab = replace_pair(most_frequent, vocab) if space else replace_pair_no_space(most_frequent, vocab)
        #vocab = replace_pair_no_space(most_frequent, vocab, indexes)
        
        tokens, idx, pairs = update_tokens(tokens, idx, pairs, most_frequent)


        # TODO maybe write later?
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
