import os
from os.path import join
import sys
import codecs

# import global variables from settings.py
sys.path.insert(1, join(sys.path[0], '..'))
from settings import *


def map_subword_to_word(corpus: list, bpes: dict, lang: str) -> dict:
    '''
    Input: list of sentences with subword separation. Can be in space mode or not.
    corpus = [
        'b u t▁this▁is▁no t▁w hat▁hap pen s▁.',
        'th e▁ ice▁cre am_.',
        ...
    ]
    Output: dictionary of each language and 
    a list of indexes pointing to which word each element (t▁w) belongs to
    bpes = {
        source:
        [
            [[0], [0], [0,1,2,3], [3,4], [4,5], [5], [5,6]],
            [[0], [0], [1,2], [2]],
            ...
        ],
        target:
        [
            ...
        ],
    }
    '''

    bpes[lang] = []
    for sent in corpus:
        sent_bpes = []

        # start at 0 in no space mode, start at -1 in space mode
        j = 0 if sent[0] != word_sep else -1
        
        for word in sent.split():
            if word == word_sep:
                # word is simply '_', doesn't belong to anything
                j += 1
                sent_bpes.append([])
                continue

            word_count = word.count(word_sep)
            if word_count == 0:
                sent_bpes.append([j])
                continue

            # multiple words in the element: t▁this▁is▁no -> [0,1,2,3]
            if word[0] == word_sep:
                # word starts with '_' but there are no elements of the previous word in it
                j += 1
                word_count -= 1

            if word[-1] == word_sep:
                # word ends with '_' but there are no elements of the next word in it
                sent_bpes.append(list(range(j, j + word_count)))
            else:
                sent_bpes.append(list(range(j, j + word_count + 1)))

            j += word_count

        bpes[lang].append(sent_bpes)
    return bpes


def load_and_map_segmentations(num_symbols: str, i: int =-1) -> dict:
    bpes = {}

    for lang in [source, target]:
        if params[lang]['bpe']:
            segmentpath = join(bpedir, 'segmentations', f"{lang}_{num_symbols}{'_'+str(i) if i != -1 else ''}.bpe")
            argsinput = codecs.open(segmentpath, encoding='utf-8')
            bpes = map_subword_to_word(argsinput, bpes, lang)
        else:
            argsinput = codecs.open(inputpath[lang], encoding='utf-8')
            bpes[lang] = []
            for line in argsinput:
                line = line.split('\t')[1].strip('\r\n ').split(' ')
                bpes[lang].append([[x] for x in list(range(len(line)))])
    return bpes


def bpe_word_align(bpes: dict, bpe_aligns: list) -> str:
    '''
    Input: dictionary of bpes obtained as output of map_subword_to_word()
    Output: list of word alignments and their indexes
        "
            0   0-0 0-1 1-1 1-2 3-1 2-4 \n
            1   0-0 1-0 1-1 2-1 \n
            ...
        "
    '''
    all_word_aligns = ''
    for i, (sent1, sent2, bpe_al) in enumerate(zip(bpes[source], bpes[target], bpe_aligns)):
        word_aligns = set()
        # iterate each alignment
        for al in bpe_al.split('\t')[1].split():
            firstal, secondal = al.split('-')
            for el1 in sent1[int(firstal)]:
                for el2 in sent2[int(secondal)]:
                    word_aligns.add(f"{el1}-{el2}")

        all_word_aligns += f"{i}\t{' '.join(word_aligns)}\n"
    return all_word_aligns
