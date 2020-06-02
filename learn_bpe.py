#!/usr/bin/env python

# inspired by https://gist.github.com/akashjaswal/ba302b943dfb4e56ace0d5761d01b9cf#file-bpe-py
import os
from os.path import join
import re
import sys
import codecs
from collections import defaultdict, Counter
from tqdm import tqdm

# import global variables from settings.py
from settings import *

def build_vocab(corpus):
    """
    Read corpus and return dictionary containing each word and its frequency in the corpus.
    Words are separated by spaces.
    Each word has a u'\u2581' symbol at the beginning to signal it's the beginning of the word.
    """

    tokens = []
    #vocab = Counter()
    for line in corpus:
        line = line.split('\t')[1].strip('\r\n ').replace('.', ' .').split()
        line[0] = str.lower(line[0])
        
        '''
        for word in line:
            vocab[u'\u2581' + ' '.join(word)] += 1
        '''
        tokens.append(' '.join([u'\u2581' + ' '.join(word) for word in line]))

    return tokens


def build_vocab_ns(corpus):
    """
    Read corpus and return dictionary containing each word and its frequency in the corpus.
    Words are separated by spaces.
    Each word has a u'\u2581' symbol at the beginning to signal it's the beginning of the word.
    """

    tokens = []
    for line in corpus:
        line = line.split('\t')[1].strip('\r\n ').replace('.', ' .').split()
        line[0] = str.lower(line[0])
        tokens.append(u' \u2581 '.join([' '.join(word) for word in line]))

    return tokens


def get_stats(tokens):
    """
    Count frequency of all symbol pairs
    """

    '''
    pairs = Counter()
    for word, freq in vocab.items():
        symbols = word.split()
        # Counting up occurrences of pairs
        for i in range(len(symbols) - 1):
            pairs[symbols[i], symbols[i + 1]] += freq

    return pairs
    '''

    pairs = Counter()
    idx = defaultdict(lambda: defaultdict(int))
    '''
    idx = {
        # keys are bigrams
        ('t', 'h'): {
            # keys are indexes in corpus, values are frequency of appearance
            0: 2,
            1: 3,
            ...
        }
        ...
    }
    '''
    for i, sent in enumerate(tokens):
        words = sent.split(u' \u2581')
        for word in words:
            if word[0] != u'\u2581':
                word = u'\u2581' + word
            symbols = word.split()
            for j in range(len(symbols) - 1):
                new_pair = symbols[j], symbols[j + 1]
                pairs[new_pair] += 1
                idx[new_pair][i] += 1

    return pairs, idx


def get_stats_ns(tokens):
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


def update_tokens(tokens, idx, pairs, pair):

    def update_merge(pairs, idx, pair, new_bgm=-1):
        # remove 1 from pair freq. delete if freq == 0
        pairs[pair] -= 1
        if pairs[pair] == 0: del pairs[pair]

        # delete 1 from pair freq. in idx. if freq == 0, delete entry for that sentence
        # if pair isn't present in any sentence (idx[pair] is empty), delete idx[pair]
        idx[pair][i] -= 1
        if idx[pair][i] == 0: del idx[pair][i]
        if len(idx[pair]) == 0: del idx[pair]

        # add new bigram to pairs and idx
        if new_bgm != -1:
            pairs[new_bgm] += 1
            idx[new_bgm][i] += 1

        return pairs, idx

    bigram = ' '.join(pair)
    merged_bigram = ''.join(pair)
    p = re.compile(r'(?<!\S)' + re.escape(bigram) + r'(?!\S)')

    # only iterate the corpus indexes where the pair to be merged is present
    for i in list(idx[pair].keys()).copy():

        sent = tokens[i] = p.sub(merged_bigram, tokens[i])
        sent = sent.split(merged_bigram)

        # iterate occurrences of merged_bigram in sent
        # where due to the merge, the freqs of previous and after tokens
        # needs to be reduced by 1
        for k in range(len(sent[:-1])):

            # obtain previous pair to delete, since pair is being merged
            # only do it if sent[k] isn't a space
            # and in space mode, if the merged_bigram isn't the beginning of the word.
            # in this case, we don't want the last letter from the prev word to be merged with
            # our current pair. ... e _t h ... we dn't want to consider ('e', '_t')
            if len(sent[k]) > 1 and u'\u2581' not in pair[0][0]:
                prev = (sent[k].split()[-1], pair[0])
                new_bgm = (prev[0], merged_bigram)
                pairs, idx = update_merge(pairs, idx, prev, new_bgm)

            # same for the after token only if the after token isn't a new word
            if len(sent[k+1]) > 1 and u'\u2581' not in sent[k+1].split()[0]:
                after = (pair[1], sent[k+1].split()[0])
                new_bgm = (merged_bigram, after[1])
                pairs, idx = update_merge(pairs, idx, after, new_bgm)

            # delete freq of merged bigram
            pairs, idx = update_merge(pairs, idx, pair)

    return tokens, idx, pairs


def update_tokens_ns(tokens, idx, pairs, pair):

    bigram = ' '.join(pair)
    merged_bigram = ''.join(pair)
    lenb = len(merged_bigram)

    # only iterate the corpus indexes where the pair to be merged is present
    for i in idx[pair].copy():

        sent = tokens[i] = tokens[i].replace(bigram, merged_bigram)

        # iterate the merged sentence to find previous and after tokens to update
        for j in range(len(sent[:-lenb])):

            if sent[j:j+lenb] != merged_bigram:
                continue
            
            # condition to exclude the first character in the sentence
            if j != 0:
                prev = (sent[:j].split()[-1], pair[0])

                # remove token before the merged pair
                pairs[prev] -= 1
                idx[prev].discard(i) # .discard() instead of .remove() because it's safer when i isn't present in set
                if pairs[prev] == 0:
                    del pairs[prev]
                    del idx[prev]
                
                # add new bigram to pairs and indexes
                new_bgm = (prev[0], merged_bigram)
                pairs[new_bgm] += 1
                idx[new_bgm].add(i)

            # condition to exclude the last character in the sentence
            if j != len(sent):
                after = (pair[1], sent[j+lenb:].split()[0])

                # remove token before the merged pair
                pairs[after] -= 1
                idx[after].discard(i)
                if pairs[after] == 0:
                    del pairs[after]
                    del idx[after]
                
                # add new bigram to pairs and indexes
                new_bgm = (merged_bigram, after[1])
                pairs[new_bgm] += 1
                idx[new_bgm].add(i)

    # delete bigram that was merged from pairs and idx
    del pairs[pair]
    del idx[pair]

    return tokens, idx, pairs


def learn_bpe(corpus, bpe_model, num_symbols):
    """
    Learn num_symbols BPE operations from vocabulary, and write to bpe_model.
    """
    # 1. split corpus into characters, count frequency
    tokens = build_vocab(corpus) if space else build_vocab_ns(corpus)

    # 2. count bigrams in corpus
    pairs, idx = get_stats(tokens) if space else get_stats_ns(tokens)

    most_frequent_merges = []
    for i in tqdm(range(num_symbols)):

        # 3. merge symbols
        most_frequent = pairs.most_common(1)[0][0]

        # if the most frequent merge was already done, delete entries in pairs and idx and continue
        if most_frequent in most_frequent_merges:
            pairs.pop(most_frequent, None)
            idx.pop(most_frequent, None)
            continue
        else:
            most_frequent_merges.add(most_frequent)

        tokens, idx, pairs = update_tokens(tokens, idx, pairs, most_frequent) if space else \
                             update_tokens_ns(tokens, idx, pairs, most_frequent)

        if not pairs:
            break

    return most_frequent_merges, i


if __name__ == '__main__':

    for lang in [source, target]:

        # check if a BPE model for this language exists
        # if so, only create new BPE model if num_symbols > symbols in the model
        model_path = join(datadir, lang+('' if space else '_ns')+'.model')
        if os.path.isfile(model_path):
            bpe_model = codecs.open(model_path, encoding='utf-8').readlines()
            if bpe_model:
                model_symbols = bpe_model[0].strip('\r\n').split()[1]
                if num_symbols <= int(model_symbols):
                    print(f"There already exists a model with at least {num_symbols} symbols")
                    sys.exit()
        
        argsinput = codecs.open(inputpath[lang], encoding='utf-8')
        bpe_model = codecs.open(model_path, 'w', encoding='utf-8')

        print(f"Learning {num_symbols} BPE symbols for lang={lang}, space mode={space}")
        most_freq_merges, i = learn_bpe(argsinput, bpe_model, num_symbols)

        # 4. write merge list to file
        bpe_model.write(f"{lang} {i}\n")
        bpe_model.write('\n'.join(' '.join(item) for item in most_freq_merges))
