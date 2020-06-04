#!/usr/bin/env python

import re
import sys
import codecs
from tqdm import tqdm
from os.path import join
from collections import defaultdict, Counter

# import global variables from settings.py
from settings import *

def build_vocab(corpus: list) -> list:
    """
    Read corpus, strip index and new line characters.
    In space mode, each word has a u'\u2581' symbol at the beginning to signal it's the beginning of the word.
    In no space mode, there's no signal at the beginning of the word but word are joined by u'\u2581'.
    """

    tokens = []
    for line in corpus:
        line = line.split('\t')[1].strip('\r\n ').replace('.', ' .').split()
        line[0] = str.lower(line[0])

        if space:
            # add u'\u2581' to each beginning of word and join by space
            tokens.append( ' '.join([u'\u2581' + ' '.join(word) for word in line]))
        else:
            # join all words by u'\u2581'
            tokens.append(u' \u2581 '.join([' '.join(word) for word in line]))

    return tokens


def get_stats(tokens: list) -> (Counter, dict):
    """
    Count frequency of all bigrams, the indexes where they occur and the frequency per index.
    pairs = {
        ('s', 'h'): 5,
        ('h', 'e'): 6
    }

    idx = {
        ('t', 'h'): {
            # keys are indexes in corpus, values are frequency of appearance
            0: 2,
            1: 3,
            ...
        }
        ...
    }
    In space mode, the last token '.' or u'\u2581'. isn't merged with anything.
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
            # get stats for each word independently, no bigrams between different words
            for word in sent[1:].split(u' \u2581'):
                pairs, idx = get_pairs_idx(pairs, idx, u'\u2581' + word)
        else:
            # get bigram stats for the whole sentence
            pairs, idx = get_pairs_idx(pairs, idx, sent)

    return pairs, idx


def update_tokens(tokens, idx, pairs, pair):

    def update_freqs(pairs, idx, pair, new_pair=-1):

        # decrease freq from pairs
        pairs[pair] -= 1
        if pairs[pair] <= 0: del pairs[pair]

        # decrease freq from idx
        idx[pair][i] -= 1
        if idx[pair][i] <= 0: del idx[pair][i]
        if len(idx[pair]) <= 0: del idx[pair]

        if new_pair != -1:
            pairs[new_pair] += 1
            idx[new_pair][i] += 1

        return pairs, idx

    merged_pair = ''.join(pair)
    p = re.compile(r'(?<!\S)' + re.escape(' '.join(pair)) + r'(?!\S)')

    # only iterate the corpus indexes where the pair to be merged is present
    for i in list(idx[pair]).copy():

        # merge pair in the sentence
        sent = p.sub(merged_pair, tokens[i])

        # sentence remains unchanged. Delete pair from pairs and idx and continue
        if sent == tokens[i]:
            del pairs[pair]
            del idx[pair][i]
            if len(idx[pair]) <= 0:
                del idx[pair]
            continue

        tokens[i] = sent

        '''
        iterate sent by the position the merged_pair occurs. 
        in each position, we need to reduce freq of previous and after tokens
        sentence before merge: 'h e l l o', pair: ('e', 'l')
        merged sent = 'h el l o'
        sent.split(merged_pair) -> ['h ', ' l o']
        we iterate the splitted sentence and in each occasion
        * decrease freq of previous token ('h', 'e')
            * create new token ('h', 'el')
        * decrease freq of after token ('l', 'l')
            * create new token ('el', 'l')
        * decrease freq of merged pair ('e', 'l')
        '''
        sent = sent.split(merged_pair)
        for k in range(len(sent[:-1])):

            if sent[k].split() and (sent[k][-1] == ' ' and u'\u2581' not in pair[0][0] if space else True):
                '''
                conditions to update the **previous** token:
                * if sent[k] isn't empty. if it is, there's no previous token to update.
                * in space mode, if the merged_pair isn't the beginning of the word.
                    * in this case, we don't want the last letter from the prev word to be merged with
                    * our current pair. ... e _t h ... we don't want to consider ('e', '_t')
                '''
                prev = (sent[k].split()[-1], pair[0])
                new_pair = (prev[0], merged_pair)
                pairs, idx = update_freqs(pairs, idx, prev, new_pair)

            if space and not sent[k+1].split() and u'\u2581' not in pair[0][0]:
                '''
                conditions to update the **after** token when merged bigrams are consecutive:
                * in space mode specifically, when the pair's first character isn't the beginning of the word
                * and when the next token is empty
                * we're dealing with consecutive merged pairs, merged_pair = ('ssi'), sent= 'm i ssi ssi p p i'
                    * in this case, we delete the token between the merged_pair: ('i', 's')
                    * and create a new pair ('ssi', 'ssi')
                '''
                after = (pair[1], pair[0])
                new_pair = (merged_pair, merged_pair)

            elif sent[k+1].split() and (u'\u2581' not in sent[k+1].split()[0] if space else True):
                '''
                conditions to update the **after** token in a more general case:
                * if sent[k] isn't empty. if it is, there's no after token to update.
                * in space mode, if the after token is a new word, we don't want to consider it.
                '''
                after = (pair[1], sent[k+1].split()[0])
                new_pair = (merged_pair, after[1])
                pairs, idx = update_freqs(pairs, idx, after, new_pair)

            # decrease freq of merged bigram
            pairs, idx = update_freqs(pairs, idx, pair)

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

        # 4. Merge the most frequent merge, update pairs 
        tokens, idx, pairs = update_tokens(tokens, idx, pairs, most_frequent)

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
