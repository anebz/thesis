#!/usr/bin/env python3
import os
import re
import sys
import json
import codecs
from tqdm import tqdm
from os.path import join
from collections import defaultdict, Counter

# import global variables from settings.py
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from settings import *

threshold = 0.1
most_freq_segments = 20000
r = re.compile('[^a-zA-Z]')

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
    source_line = source_line.strip('\n')
    try:
        source_line = source_line.split('\t')[1]
    except:
        pass
    # lower the first character in the sentence
    source_line = source_line[0].lower() + source_line[1:]
    source_line = r.sub(' ', source_line)

    # map german characters to English equivalents
    char_map = {ord('ä'): 'ae', ord('ü'): 'ue', ord('ö'): 'oe', ord('ß'): 'ss'}
    target_line = target_line.translate(char_map).strip('\n')
    return source_line.split(), target_line.split()


def parse_mapping(symb: int) -> defaultdict(Counter):
    '''
    obtain most common mappings from source language to target language,
    and print the mappings and the percentage they appear in. Steps:
    1. Open alignment file, source file, target file
    2. Iterate these 3 and for each English unit, obtain its corresponding German mapping according to the alignment
    Output: {
        "we": {"wi": "0.1833", "wir": "0.1497", ...},
        "do": {"i": "0.0715", "n": "0.0709", "ch": "0.0582", ...}, ...
    }
    For example, "wi" constitutes to 18.33% of the mappings for "we".
    '''

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
                # only consider English units with 1+ letters
                if len(r.sub(' ', unit_source)) > 1:
                    for idx in almaps[i]:
                        if len(target_line[idx].replace(word_sep, '')) > 1:
                            unit_maps[unit_source][target_line[idx]] += 1

    # get the segments ordered by number of mappings
    counter_map = {}
    for k, v in unit_maps.items():
        counter_map[k] = sum(v.values())
    counter_map = [k for k, v in reversed(sorted(counter_map.items(), key=lambda item: item[1]))]
    
    # get only the most frequent segments
    shorter_unit_map = {}
    for segment in counter_map[:most_freq_segments]:
        v = unit_maps[segment]
        all_sum = sum(v.values())
        shorter_unit_map[segment] = {i: f"{v[i]/all_sum:.4f}" for i, _ in v.most_common(20)}

    return shorter_unit_map


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


def most_common_substring(lst: list) -> str:
    '''
    link: https://stackoverflow.com/a/32611507/4569908
    Given a list of strings, returns the most common substring
    Input: lst = ["wi", "wir▁", "ir▁", "wir", "▁wir▁", "uns", "en", "mu"]
    Output: "wi"
    '''
    substrs = lambda x: Counter(x[i:i+j] for i in range(len(x)) for j in range(1, len(x) - i + 1))
    subs = Counter()
    for val in lst:
        subs += substrs(val)
    return list(filter(lambda elem: len(elem) > 1, list(zip(*subs.most_common()))[0]))[0]


def aggregate_mappings(unit_maps: defaultdict(Counter)) -> dict:
    all_maps = {}
    subwords = []
    for eng_word, deu_maps in unit_maps.items():
        # obtain the longest sequence that contains the most common unit
        most_common_unit = most_common_substring(deu_maps)
        for longest in sorted(deu_maps, reverse=True):
            if most_common_unit in longest:
                break
        
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
        if len(best_mapping) > 1:
            all_maps[eng_word] = best_mapping
            if best_mapping not in subwords:
                subwords.append(best_mapping)
    return all_maps, subwords


if __name__ == "__main__":

    symb = merges[0]
    unit_maps = parse_mapping(symb)
    all_maps, subwords = aggregate_mappings(unit_maps)

    # join subwords
    if os.path.isfile(join(rootdir, 'data', f'subwords.txt')):
        print("Merging with previous subword list")
        with open(join(rootdir, 'data', f'subwords.txt'), 'r', encoding='utf8') as subwordf:
            prev_subwords = [line.strip('\r\n ') for line in subwordf.readlines()]

        for subw in subwords:
            if subw not in prev_subwords:
                prev_subwords.append(subw)
        subwords = prev_subwords

    print(f"Writing {len(subwords)} subwords")
    with open(join(rootdir, 'data', 'subwords.txt'), 'w', encoding='utf8') as out:
        out.write('\n'.join(subwords))
