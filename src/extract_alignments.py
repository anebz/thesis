#!/usr/bin/env python3
import os
import sys
import codecs
from os.path import join

# import global variables from settings.py
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from settings import *


def create_parallel_text(corpusfile: list, vocab_size: int, i: int):
    target_bpe = codecs.open(join(bpedir, 'segmentations', f"{target}_{vocab_size}{'_'+str(i) if params[target]['dropout'] > 0 else ''}.bpe"), encoding='utf-8')
    with codecs.open(join(bpedir, mode, f"{vocab_size}_{i}.txt"), "w") as pfile:
        for sl, tl in zip(corpusfile, target_bpe):
            pfile.write(f"{sl} ||| {tl}")
    return


def create_fwd_rev_files(outpath: str):
    if mode == "fastalign":
        os.system(f"{fastalign_path} -i {outpath}.txt -v -d -o > {outpath}.fwd")
        os.system(f"{fastalign_path} -i {outpath}.txt -v -d -o -r > {outpath}.rev")
    elif mode == "eflomal":
        os.system(f"cd {eflomal_path}; python align.py -i {outpath}.txt --model 3 -f {outpath}.fwd -r {outpath}.rev")
    return


def create_gdfa_file(outpath: str):
    # create gdfa file from .fwd and .rev
    os.system(f"{atools_path} -i {outpath}.fwd -j {outpath}.rev -c grow-diag-final-and > {outpath}_unnum.gdfa")

    # parse _unnum.gdfa to .gdfa with "\t" separator
    with codecs.open(f"{outpath}_unnum.gdfa", "r", "utf-8") as fi:
        with codecs.open(f"{outpath}.gdfa", "w", "utf-8") as fo:
            for ii, line in enumerate(fi):
                fo.write(f"{ii}\t{line.strip()}\n")

    # delete unnecessary files
    os.system(f"rm {outpath}_unnum.gdfa; rm {outpath}.fwd; rm {outpath}.rev; rm {outpath}.txt")
    return


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


def load_and_map_segmentations(vocab_size: str, i: int =-1) -> dict:
    bpes = {}

    for lang in [source, target]:
        if params[lang]['bpe']:
            segmentpath = join(bpedir, 'segmentations', f"{lang}_{vocab_size}{'_'+str(i) if params[lang]['dropout'] > 0 else ''}.bpe")
            argsinput = codecs.open(segmentpath, encoding='utf-8')
            bpes = map_subword_to_word(argsinput, bpes, lang)
        else:
            argsinput = codecs.open(inputpath[lang], encoding='utf-8')
            bpes[lang] = []
            for line in argsinput:
                try:
                    line = line.split('\t')[1]
                except:
                    pass
                line = line.strip('\r\n ').split(' ')
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


def extract_alignments(corpusfile: list, i: int = -1, input_mode: bool = False):
    for vocab_size in merges:

        print(f"Extracting alignments, i={i}, vocab_size={vocab_size}\n")
        outpath = join(bpedir, mode, f"{vocab_size}{'_'+str(i) if i != -1 else ''}")

        create_parallel_text(corpusfile, vocab_size, i)
        create_fwd_rev_files(outpath)
        create_gdfa_file(outpath)

        if input_mode:
            break

        # map alignment from subword to word
        bpes = load_and_map_segmentations(vocab_size, i)
        all_word_aligns = bpe_word_align(bpes, codecs.open(outpath+'.gdfa', encoding='utf-8'))
        os.system(f"rm {outpath}.gdfa")
        codecs.open(outpath+'.wgdfa', 'w', encoding='utf-8').write(all_word_aligns)
        print("\n\n")
    return
