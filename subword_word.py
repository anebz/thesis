import os
from os.path import join
import glob
import codecs
from tqdm import tqdm

# import global variables from lib/__init__.py
from lib import *


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
            'eng':
            [
                [0, 1, 2, 2, 3, 3, 3, 4],
                [0, 0, 1, 2, 3, 4, 5],
                ...
            ],
            'deu':
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
    os.chdir(join(bpepath, 'segmentations'))
    for inputpath in glob.glob("*_"+num_symbols+('_'+i if i!=-1 else '')+".bpe"):
        lang = inputpath.split('.')[0].split('_')[0]
        if german_bpe and lang == 'eng':
            argsinput = codecs.open(
                join(datapath, 'input/eng_with_10k.txt'), encoding='utf-8')
            bpes['eng'] = []
            for line in argsinput:
                line = line.split('\t')[1].strip('\r\n ').split(' ')
                bpes['eng'].append(list(range(len(line))))
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
    for sent1, sent2, bpe_al in zip(bpes['eng'], bpes['deu'], bpe_aligns):
        word_aligns = ''
        # iterate each alignment
        # bpe_al.split('\t')[1] to remove the index in the alignment file .gdfa
        for al in bpe_al.split('\t')[1].split():
            firstal, secondal = al.split('-')
            new_al = str(sent1[int(firstal)]) + '-' + str(sent2[int(secondal)])
            # skip already seen word alignments
            if not new_al in word_aligns:
                word_aligns += new_al + ' '
        all_word_aligns += str(i) + "\t" + word_aligns[:-1] + "\n"
        i += 1
    return all_word_aligns


if __name__ == "__main__":

    german_bpe = False
    os.chdir(bpepath)

    for alfile in tqdm(glob.glob("fastalign/[0-9]*.gdfa")):
        if german_bpe ^ ('_deu' in alfile) or '_word' in alfile:
            continue

        num_symbols = alfile.split(".")[0].split(os.sep)[1]
        i = -1
        if dropout:
            num_symbols, i = num_symbols.split('_')
        num_symbols = num_symbols.replace('_deu', '')
        bpes = load_and_map_segmentations(num_symbols, i)

        argsalign = codecs.open(join(bpepath, alfile), encoding='utf-8')
        all_word_aligns = bpe_word_align(bpes, argsalign)

        outputpath = join(bpepath, 'fastalign',num_symbols+('_'+i if i!=-1 else '')+'_word.gdfa')
        argsoutput = codecs.open(outputpath, 'w', encoding='utf-8')
        argsoutput.write(all_word_aligns)
