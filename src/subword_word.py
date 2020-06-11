import os
from os.path import join
import sys
import codecs

# import global variables from settings.py
sys.path.insert(1, join(sys.path[0], '..'))
from settings import *


def map_subword_to_word(corpus, bpes, lang):
    '''
    SPACE MODE
    Input: list of sentences with subword separation
    corpus =  [
        '_We _do _no t _be li eve _.',
        '_Thi s _is _a _sent ence _.',
        ...
    ]
    Output: dictionary of each language and 
    a list of indexes pointing to which word each element (_do) belongs to
    bpe = {
        source:
        [
            [0, 1, 2, 2, 3, 3, 3, 4],
            [0, 0, 1, 2, 3, 4, 5],
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
        mapping = [0]
        i = 0
        for subw in sent.split()[1:]:
            if subw[0] == word_sep:
                i += 1
            mapping.append(i)
        bpes[lang].append(mapping)
    return bpes


def map_multiple_to_word(corpus, bpes, lang):
    '''
    NO SPACE MODE
    Input: list of sentences with subword separation
    corpus =  [
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
        j = 0
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


def load_and_map_segmentations(num_symbols, i=-1):

    bpes = {}
    os.chdir(join(bpedir, 'segmentations'))
    for lang in [source, target]:
        segmentpath = lang+'_'+str(num_symbols)+('_'+str(i) if i != -1 else '')+'.bpe'

        if target_bpe and lang == source:
            argsinput = codecs.open(inputpath[source], encoding='utf-8')
            bpes[source] = []
            for line in argsinput:
                line = line.split('\t')[1].strip('\r\n ').split(' ')
                bpes[source].append(list(range(len(line))))
        elif source_bpe and lang == target:
            argsinput = codecs.open(inputpath[target], encoding='utf-8')
            bpes[target] = []
            for line in argsinput:
                line = line.split('\t')[1].strip('\r\n ').split(' ')
                bpes[target].append(list(range(len(line))))
        else:
            argsinput = codecs.open(segmentpath, encoding='utf-8')
            if space:
                bpes = map_subword_to_word(argsinput, bpes, lang)
            else:
                bpes = map_multiple_to_word(argsinput, bpes, lang)
    return bpes


def bpe_word_align(bpes, bpe_aligns):
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
            if space:
                new_al = str(sent1[int(firstal)]) + '-' + str(sent2[int(secondal)])
                word_aligns.add(new_al)
            else:
                for el1 in sent1[int(firstal)]:
                    for el2 in sent2[int(secondal)]:
                        new_al = str(el1) + '-' + str(el2)
                        word_aligns.add(new_al)

        all_word_aligns += str(i) + "\t" + ' '.join(word_aligns) + "\n"
    return all_word_aligns
