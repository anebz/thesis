#!/usr/bin/env python3
import os
import sys
import json
import codecs
from tqdm import tqdm
from os.path import join
from collections import defaultdict, Counter

# import global variables from settings.py
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from settings import *

threshold = 0.15

def parse_alignment(al_line: str) -> defaultdict(list):
    '''
    Parse an alignment file:
    Input: '0-0 0-1 1-0 2-1...\n'
    Output: {0: [0, 1], 1: [0], 2: [1], ...}
    '''
    almaps = defaultdict(list)
    for al in al_line.strip('\n').split('\t')[1].split():
        firstal, secal = al.split('-')
        almaps[int(firstal)].append(int(secal))
    return almaps


def parse_segmentations(source_line: str, target_line: str) -> (str, str):
    '''
    Parse segmentation file for source and target languages. For English, for example:
    Input: '0   _This _is _a _sentence\n'
    Output: ['_This', '_is', '_a', '_sentence']
    '''
    source_line = source_line.strip('\n').split('\t')[1]

    # lower the first character in the sentence
    source_line = source_line[0].lower() + source_line[1:]

    # map german characters to English equivalents
    char_map = {ord('ä'): 'ae', ord('ü'): 'ue', ord('ö'): 'oe', ord('ß'): 'ss'}
    target_line = target_line.translate(char_map).strip('\n')
    return source_line.split(), target_line.split()


def parse_mapping(unit_maps: defaultdict(list)) -> defaultdict(list):
    '''
    obtain most common mappings and print the mappings and the percentage they appear in.
    For example, "wi" appears in 18.33% of all mappings.
    Input: [
        "we": Counter("w": 2, "wi": 2, "ir": 3, "r": 2, "wi": 3, "wir": 1, ...),
        "do": Counter("i": 2, "n": 3, "ch": 1, ...), ...
    ]
    Output: {
        "we": {"wi": "0.1833", "wir": "0.1497", ...},
        "do": {"i": "0.0715", "n": "0.0709", "ch": "0.0582", ...}, ...
    }
    '''
    
    for k, v in unit_maps.items():
        all_sum = sum(v.values())
        unit_maps[k] = {i: f"{v[i]/all_sum:.4f}" for i, _ in v.most_common(15)}
    return unit_maps


def max_subarray(arr: list) -> list:
    '''
    Given an array, find the subarray with the maximum value with a certain threshold
    Example: threshold = 2
    Input: [0, 1, 2, 1, 3, 4, 1]
    Output: range(4, 6) (indices for the subarray [3, 4])
    '''
    count, maxval = 0, 0
    beg, end = -1, 0
    for i, num in enumerate(arr):
        count += num
        if num <= threshold:
            count = 0
        elif count > maxval:
            maxval = count
            beg = i if beg == -1 else beg
            end = i + 1
    return range(beg, end)


def aggregate_mappings(unit_maps: defaultdict(Counter)) -> dict:
    all_maps = {}
    for eng_word, deu_maps in unit_maps.items():
        # obtain the longest sequence
        longest = max(deu_maps, key=lambda x: len(x))
        # scores for each character
        score = [0 for i in range(len(longest))]

        # update scores with the scores of the words
        for word in deu_maps:
            if word in longest:
                # update scores in these indexes
                for i in range(longest.index(word), longest.index(word) + len(word)):
                    score[i] += float(deu_maps[word])

        # get the characters with the highest scores. maximum subarray of the scores array
        best_mapping = ''.join(list(map(longest.__getitem__, max_subarray(score))))
        all_maps[eng_word] = best_mapping
    return all_maps


if __name__ == "__main__":

    symb = merges[0]
    unit_maps = defaultdict(Counter)
    for it in tqdm(range(dropout_samples)):
        alfile = codecs.open(join(bpedir, mode, f'{symb}_{it}.gdfa'), 'r')
        sourcefile = codecs.open(inputpath[source], 'r')
        targetfile = codecs.open(join(bpedir, 'segmentations', f'{target}_{symb}_{it}.bpe'), 'r', 'utf-8')

        for al_line, source_line, target_line in zip(alfile, sourcefile, targetfile):
            almaps = parse_alignment(al_line)
            source_line, target_line = parse_segmentations(source_line, target_line)

            # obtain segmentation mappings and save to unit_maps
            for i, unit_source in enumerate(source_line):
                for idx in almaps[i]:
                    sent = target_line[idx].replace(word_sep, '')
                    if len(sent) > 1:
                        unit_maps[unit_source][sent] += 1

    unit_maps = parse_mapping(unit_maps)

    with open(join(rootdir, 'mapping.json'), 'w', encoding='utf8') as out:
        json.dump(unit_maps, out, indent=2, ensure_ascii=False)

    all_maps = aggregate_mappings(unit_maps)

    with open(join(rootdir, 'best_mappings.json'), 'w', encoding='utf8') as out:
        json.dump(all_maps, out, indent=2, ensure_ascii=False)
