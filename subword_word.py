import os
from os.path import join
import glob
import codecs

# import global variables from settings.py
from settings import *


def subword_align_to_word(corpus, bpes, lang):
    '''
    Input: list of sentences with subword separation
        [
            '_We _do _no t _be li eve _.',
            '_Thi s _is _a _sent ence _.',
            ...
        ]
    Output: dictionary of each language and 
    a list of vectors pointing to which word each subword belongs to
        {
            lang_1:
            [
                [0, 1, 2, 2, 3, 3, 3, 4],
                [0, 0, 1, 2, 3, 4, 5],
                ...
            ],
            lang_2:
            [
                [0, 1, 2, 3, 3, 4, 4, 5],
                [0, 0, 1, 1, 2, 3, 4],
                ...
            ],
        }
        
    '''
    if lang in bpes:
        return bpes
    bpes[lang] = []
    for sent in corpus:
        sent = sent.split()
        subwords = [0]
        i = 0
        for subw in sent[1:]:
            if subw[0] == u'\u2581':
                i += 1
            subwords.append(i)
        bpes[lang].append(subwords)
    return bpes


def load_and_map_segmentations(num_symbols, i=-1):

    bpes = {}
    os.chdir(join(bpedir, 'segmentations'))
    for inputpath in glob.glob("*_"+str(num_symbols)+('_'+str(i) if i!=-1 else '')+".bpe"):
        lang = inputpath.split('.')[0].split('_')[0]
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
            argsinput = codecs.open(inputpath, encoding='utf-8')
            bpes = subword_align_to_word(argsinput, bpes, lang)
    return bpes


def bpe_word_align(bpes, bpe_aligns):
    '''
    Input: dictionary of bpes obtained as output of subword_align_to_word()
    Output: list of word alignments and their indexes
        "
            0   0-0 0-1 1-1 1-2 3-1 2-4 \n
            1   0-0 1-0 1-1 2-1 \n
            ...
        "
    '''
    all_word_aligns = ''
    # iterate all sentences
    i = 0
    for sent1, sent2, bpe_al in zip(bpes[source], bpes[target], bpe_aligns):
        word_aligns = []
        # iterate each alignment
        # bpe_al.split('\t')[1] to remove the index in the alignment file .gdfa
        for al in bpe_al.split('\t')[1].split():
            firstal, secondal = al.split('-')
            new_al = str(sent1[int(firstal)]) + '-' + str(sent2[int(secondal)])
            # skip already seen word alignments
            if not new_al in word_aligns:
                word_aligns.append(new_al)
        all_word_aligns += str(i) + "\t" + ' '.join(word_aligns) + "\n"
        i += 1
    return all_word_aligns
