#!/usr/bin/env python

import re
import sys
import codecs
from tqdm import tqdm
from os.path import join
from collections import defaultdict, Counter

# import global variables from settings.py
from settings import *

def build_vocab(corpus):
    """
    Read corpus and return dictionary containing each word and its frequency in the corpus.
    Words are separated by spaces.
    Each word has a u'\u2581' symbol at the beginning to signal it's the beginning of the word.
    """

    tokens = []
    for line in corpus:
        line = line.split('\t')[1].strip('\r\n ').replace('.', ' .').split()
        line[0] = str.lower(line[0])

        if space:
            tokens.append( ' '.join([u'\u2581' + ' '.join(word) for word in line]))
        else:
            tokens.append(u' \u2581 '.join([' '.join(word) for word in line]))

    return tokens


def get_stats(tokens):
    """
    Count frequency of all symbol pairs
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
    """

    def get_pairs_idx(pairs, idx, symbols):
        symbols = symbols.split()
        for j in range(len(symbols) - 1):
            new_pair = symbols[j], symbols[j + 1]
            pairs[new_pair] += 1
            idx[new_pair][i] += 1
        return pairs, idx

    pairs = Counter()
    idx = defaultdict(lambda: defaultdict(int))
    for i, sent in enumerate(tokens):
        if space:
            for word in sent.split(u' \u2581'):
                if word[0] != u'\u2581':
                    word = u'\u2581' + word
                pairs, idx = get_pairs_idx(pairs, idx, word)
        else:
            pairs, idx = get_pairs_idx(pairs, idx, sent)

    return pairs, idx


def update_tokens(tokens, idx, pairs, pair):

    def update_merge(pairs, idx, pair, new_bgm=-1):

        # remove 1 from pair freq. delete if freq == 0
        pairs[pair] -= 1
        if pairs[pair] <= 0: del pairs[pair]

        # delete 1 from pair freq. in idx. if freq == 0, delete entry for that sentence
        # if pair isn't present in any sentence (idx[pair] is empty), delete idx[pair]
        idx[pair][i] -= 1
        if idx[pair][i] <= 0: del idx[pair][i]
        if len(idx[pair]) <= 0: del idx[pair]

        # add new bigram to pairs and idx
        if new_bgm != -1:
            pairs[new_bgm] += 1
            idx[new_bgm][i] += 1

        return pairs, idx


    merged_bigram = ''.join(pair)
    p = re.compile(r'(?<!\S)' + re.escape(' '.join(pair)) + r'(?!\S)')

    # only iterate the corpus indexes where the pair to be merged is present
    for i in list(idx[pair]).copy():

        sent = p.sub(merged_bigram, tokens[i])

        # sentence remains unchanged. Delete pair from pairs and idx and continue
        if sent == tokens[i]:
            del pairs[pair]
            del idx[pair][i]
            if len(idx[pair]) <= 0:
                del idx[pair]
            continue
        else:
            tokens[i] = sent

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
            if len(sent[k]) > 1 and (sent[k][-1] == ' ' and u'\u2581' not in pair[0][0] if space else True):
                prev = (sent[k].split()[-1], pair[0])
                new_bgm = (prev[0], merged_bigram)
                pairs, idx = update_merge(pairs, idx, prev, new_bgm)


            # in space mode, case where bigram is followed by bigram: is is
            # after is: ('s', 'i') and new:bgm = ('is', 'is')
            if space and not sent[k+1].split() and (u'\u2581' not in pair[0][0] if space else True):
                after = (pair[1], pair[0])
                new_bgm = (merged_bigram, merged_bigram)
                pairs, idx = update_merge(pairs, idx, after, new_bgm)
            
            # same for the after token only if the after token isn't a new word
            if sent[k+1].split() and len(sent[k+1]) > 1 and (u'\u2581' not in sent[k+1].split()[0] if space else True):
                after = (pair[1], sent[k+1].split()[0])
                new_bgm = (merged_bigram, after[1])
                pairs, idx = update_merge(pairs, idx, after, new_bgm)

            # delete freq of merged bigram
            pairs, idx = update_merge(pairs, idx, pair)

    return tokens, idx, pairs


def learn_bpe(corpus, bpe_model, num_symbols):
    """
    Learn num_symbols BPE operations from vocabulary, and write to bpe_model.
    """
    # 1. split corpus into characters, count frequency
    tokens = build_vocab(corpus)

    # 2. count bigrams in corpus
    pairs, idx = get_stats(tokens)

    most_frequent_merges = []
    for i in tqdm(range(num_symbols)):

        try:
            # 3. merge symbols
            most_frequent = pairs.most_common(1)[0][0]
        except:
            # pairs is empty
            break

        most_frequent_merges.append(most_frequent)

        tokens, idx, pairs = update_tokens(tokens, idx, pairs, most_frequent)

    #argsout.write('\n'.join(tokens))
    return most_frequent_merges


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
        most_freq_merges = learn_bpe(argsinput, bpe_model, num_symbols)

        # 4. write merge list to file
        bpe_model.write(f"{lang} {len(most_freq_merges)}\n")
        bpe_model.write('\n'.join(' '.join(item) for item in most_freq_merges))
