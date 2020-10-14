#!/usr/bin/env python3
import os
import re
import sys
import codecs
from tqdm import tqdm
from os.path import join
from collections import defaultdict, Counter

# import global variables from settings.py
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from settings import *

def read_bpe_model(lang: str) -> (list, int):
    # check if a BPE model for this language exists
    # if so, only create new BPE model if learn_merges > symbols in the model
    model_path = join(inputdir, f"{lang}{'' if params[lang]['space'] else '_ns'}{'_scoring' if scoring else ''}.model")
    if os.path.isfile(model_path):
        bpe_model = codecs.open(model_path, encoding='utf-8').readlines()
        model_symbols = bpe_model[0].strip('\r\n').split()[1] if bpe_model else 0
    else:
        bpe_model = codecs.open(model_path, 'w', encoding='utf-8')
        model_symbols = 0
        
    return bpe_model, model_symbols


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
        line = line.split('\t')[1].strip('\r\n ').split()
        line[0] = str.lower(line[0])

        if params[lang]['space']:
            # add word_sep to each beginning of word and join by space
            tokens.append(' '.join([word_sep + ' '.join(word) for word in line]))
        else:
            # join all words by word_sep
            tokens.append(f' {word_sep} '.join([' '.join(word) for word in line]))

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


def update_tokens(lang: str, tokens: list, scores: Counter, pairs: Counter, idx: dict, pair: tuple) -> (list, Counter, Counter, dict):

    def update_freqs(scores, pairs, idx, pair, new_pair=-1):

        # decrease freq from pairs
        pairs[pair] -= 1
        scores[pair] -= 1
        if scoring:
            scores[pair] -= len(pair[0].replace(word_sep, '')) + len(pair[1].replace(word_sep, '')) - 2
        if pairs[pair] <= 0: del pairs[pair]; del scores[pair]

        # decrease freq from idx
        idx[pair][i] -= 1
        if idx[pair][i] <= 0: del idx[pair][i]
        if len(idx[pair]) <= 0: del idx[pair]

        if new_pair != -1:
            pairs[new_pair] += 1
            scores[new_pair] += 1
            if scoring:
                scores[new_pair] += len(new_pair[0].replace(word_sep, '')) + len(new_pair[1].replace(word_sep, '')) - 2
            idx[new_pair][i] += 1

        return scores, pairs, idx

    merged_pair = ''.join(pair)
    p = re.compile(r'(?<!\S)' + re.escape(' '.join(pair)) + r'(?!\S)')

    # only iterate the corpus indexes where the pair to be merged is present
    for i in list(idx[pair]).copy():

        # merge pair in the sentence
        sent = p.sub(merged_pair, tokens[i])

        # sentence remains unchanged. Delete pair from scores, pairs and idx and continue
        if sent == tokens[i]:
            del scores[pair]
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
                scores, pairs, idx = update_freqs(scores, pairs, idx, prev, new_pair)

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
                    scores, pairs, idx = update_freqs(scores, pairs, idx, after, new_pair)

            elif sent[k+1].split() and (word_sep not in sent[k+1].split()[0] if params[lang]['space'] else True):
                '''
                conditions to update the **after** token in a more general case:
                * if sent[k] isn't empty. if it is, there's no after token to update.
                * in space mode, if the after token is a new word, we don't want to consider it.
                '''
                after = (pair[1], sent[k+1].split()[0])
                new_pair = (merged_pair, after[1])
                scores, pairs, idx = update_freqs(scores, pairs, idx, after, new_pair)

            # decrease freq of merged bigram
            scores, pairs, idx = update_freqs(scores, pairs, idx, pair)

    return tokens, scores, pairs, idx


def learn_bpe(lang: str, corpus: list) -> list:
    """
    Learn BPE operations from vocabulary.
    Steps:
    1. split corpus into characters, count frequency
    2. count bigrams in corpus
    3. merge most frequent symbols
    4. Update bigrams in corpus 
    """

    tokens = read_corpus(lang, corpus)
    pairs, idx = get_stats(lang, tokens)
    scores = pairs.copy()
    most_freq_merges = []

    for i in tqdm(range(learn_merges), desc=f"learn_bpe: lang={lang}, space mode={params[lang]['space']}"):
        try:
            most_frequent = scores.most_common(1)[0]
        except:
            break
        # stop the loop if the frequency of the most common pair is 1
        if most_frequent[1] == 1:
            break

        most_freq_merges.append(most_frequent[0])
        tokens, scores, pairs, idx = update_tokens(lang, tokens, scores, pairs, idx, most_frequent[0])

    return most_freq_merges


def write_bpe(lang, most_freq_merges):
    filename = f"{lang}{'' if params[lang]['space'] else '_ns'}{'_scoring' if scoring else ''}.model"
    bpe_file = codecs.open(join(inputdir, filename), 'w', encoding='utf-8')
    bpe_file.write(f"{lang} {len(most_freq_merges)}\n")
    bpe_file.write('\n'.join(' '.join(item) for item in most_freq_merges))
    return


if __name__ == '__main__':

    for lang in [source, target]:

        argsinput = codecs.open(inputpath[lang], encoding='utf-8')
        _, model_symbols = read_bpe_model(lang)

        if learn_merges <= int(model_symbols):
            print(f"A model for lang={lang} with at least {learn_merges} symbols already exists")
            continue

        most_freq_merges = learn_bpe(lang, argsinput)
        write_bpe(lang, most_freq_merges)
