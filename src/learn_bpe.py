#!/usr/bin/env python3
import os
import re
import sys
import json
import codecs
from tqdm import tqdm
from os.path import join
from collections import defaultdict, Counter

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from settings import *


def join_best_mappings(lang: str, text: str, vocab_size: int=merges[-1]) -> list:
    if it > 0 and lang == target:
        print(f"Importing subwords from iteration {it-1}")
        with open(join(rootdir, 'data', f'subwords_{it-1}.txt'), 'r', encoding='utf-8') as subwf:
            prev_subwords = [line.strip('\r\n ') for line in subwf.readlines()]
            for elem in prev_subwords[:vocab_size]:
                text = text.replace(' '.join(list(elem)), elem)
    return text.split('\n')


def read_corpus(lang: str, corpus: list) -> list:
    """
    Read corpus, strip index and new line characters.
    In space mode, each word has a word_sep symbol at the beginning to signal it's the beginning of the word.
    example:
    tokens = [
        '▁w e ▁d o ▁n o t ▁b e l i e v e ▁t h a t ▁w e ▁s h o u l d ▁c h e r r y - p i c k ▁.',
        ...
    ]
    In no space mode, there's no signal at the beginning of the word but word are joined by word_sep.
    example:
    tokens = [
        'w e ▁ d o ▁ n o t ▁ b e l i e v e ▁ t h a t ▁ w e ▁ s h o u l d ▁ c h e r r y - p i c k ▁ .',
        ...
    ]
    """

    tokens = []
    for line in corpus:
        if line[0] == '<' or line == '\n':
            continue
        char_map = {ord('ä'): 'ae', ord('ü'): 'ue',
                    ord('ö'): 'oe', ord('ß'): 'ss'}
        line = line.translate(char_map)
        try:
            line = line.split('\t')[1]
        except:
            pass
        line = line.strip('\r\n ').split()
        line[0] = str.lower(line[0])

        if params[lang]['space']:
            # add word_sep to each beginning of word and join by space
            tokens.append(' '.join([word_sep + ' '.join(word) for word in line]))
        else:
            # join all words by word_sep
            tokens.append(f' {word_sep} '.join([' '.join(word) for word in line]))

    #tokens = join_best_mappings(lang, '\n'.join(tokens))
    return tokens


def get_stats(lang: str, tokens: list) -> (Counter, dict):
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
    In space mode, the last token '.' or word_sep. isn't merged with anything.
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
        if params[lang]['space']:
            # get stats for each word independently, no bigrams between different words
            for word in sent[1:].split(' '+word_sep):
                pairs, idx = get_pairs_idx(pairs, idx, word_sep + word)
        else:
            # get bigram stats for the whole sentence
            pairs, idx = get_pairs_idx(pairs, idx, sent)

    return pairs, idx


def update_tokens(lang: str, tokens: list, pairs: Counter, idx: dict, pair: tuple) -> (list, Counter, dict):

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

            if sent[k].split() and (sent[k][-1] == ' ' and word_sep not in pair[0][0] if params[lang]['space'] else True):
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

            if params[lang]['space'] and not sent[k+1].split() and word_sep not in pair[0][0]:
                '''
                conditions to update the **after** token when merged bigrams are consecutive:
                * in space mode specifically, when the pair's first character isn't the beginning of the word
                * and when the next token is empty
                * we're dealing with consecutive merged pairs, merged_pair = ('ssi'), sent= 'm i ssi ssi p p i'
                    * in this case, we delete the token between the merged_pair: ('i', 's')
                    * and create a new pair ('ssi', 'ssi')
                '''
                if sent[k] and sent[k][-1] == word_sep:
                    after = (word_sep+merged_pair, pair[0])
                    new_pair = -1
                else:
                    after = (pair[1], pair[0])
                    new_pair = (merged_pair, merged_pair)
                    pairs, idx = update_freqs(pairs, idx, after, new_pair)

            elif sent[k+1].split() and (word_sep not in sent[k+1].split()[0] if params[lang]['space'] else True):
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

    return tokens, pairs, idx


def learn_bpe(lang: str, corpus: list, vocab_to_learn: int) -> list:
    """
    Learn BPE operations from vocabulary.
    Steps:
    1. split corpus into characters, count frequency
    2. count bigrams in corpus
    3. merge most frequent symbols
    4. Update bigrams in corpus 
    """

    # if bpe model has already been imported, use this
    if it > 0 or vocab_to_learn < learn_vocab_size:
        tokens = corpus
    else:
        tokens = read_corpus(lang, corpus)
        tokens = join_best_mappings(lang, '\n'.join(tokens))
    pairs, idx = get_stats(lang, tokens)
    most_freq_merges = []

    for i in tqdm(range(vocab_to_learn), desc=f"learn_bpe: lang={lang}, space mode={params[lang]['space']}"):
        try:
            most_frequent = pairs.most_common(1)[0]
        except:
            break
        # stop the loop if the frequency of the most common pair is 1
        if most_frequent[1] == 1:
            break

        most_freq_merges.append(tuple(most_frequent[0]))
        tokens, pairs, idx = update_tokens(lang, tokens, pairs, idx, most_frequent[0])

    return most_freq_merges


def write_bpe(lang, most_freq_merges):
    bpe_model_fname = join(inputdir, f"{lang}{'' if params[lang]['space'] else '_ns'}{'_'+str(it) if it >= 0 else ''}.model")
    bpe_file = codecs.open(bpe_model_fname, 'w', encoding='utf-8')
    bpe_file.write(f"{lang} {len(most_freq_merges)}\n")
    bpe_file.write('\n'.join(' '.join(item) for item in most_freq_merges))
    return
