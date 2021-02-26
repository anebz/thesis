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


def parse_source(source_line: str,) -> str:
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

    return source_line.split()


def parse_mapping(vocab_size: int) -> defaultdict(Counter):
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
    source_corpus = [parse_source(line) for line in codecs.open(inputpath[source], 'r')]
    for ii in tqdm(range(dropout_samples), desc=f"vocab_size={vocab_size}"):
        alfile = codecs.open(join(bpedir, mode, f'{vocab_size}_{ii}.gdfa'), 'r')
        targetfile = codecs.open(join(bpedir, 'segmentations', f'{target}_{vocab_size}_{ii}.bpe'), 'r', 'utf-8')
        for al_line, source_line, target_line in zip(alfile, source_corpus, targetfile):
            almaps = parse_alignment(al_line)

            # map german characters to English equivalents
            char_map = {ord('ä'): 'ae', ord('ü'): 'ue', ord('ö'): 'oe', ord('ß'): 'ss'}
            target_line = target_line.translate(char_map).strip('\n').split()

            # obtain segmentation mappings and save to unit_maps
            for j, unit_source in enumerate(source_line):
                # only consider English units with 1+ letters, even without word_sep
                if len(r.sub(' ', unit_source)) > 1:
                    for idx in almaps[j]:
                        if len(target_line[idx].replace(word_sep, '')) > 1:
                            unit_maps[unit_source][target_line[idx]] += 1

    # get the segments ordered by number of mappings
    counter_map = {}
    for k, v in unit_maps.items():
        counter_map[k] = sum(v.values())
    counter_map = [k for k, v in reversed(sorted(counter_map.items(), key=lambda item: item[1]))]
    
    # get only the most frequent segments
    shorter_unit_map = {}
    for segment in counter_map:
        mappings = unit_maps[segment]
        all_sum = sum(mappings.values())
        shorter_unit_map[segment] = {k: v/all_sum for k, v in mappings.most_common(20)}

    return shorter_unit_map


def most_common_substring(lst: list) -> str:
    '''
    link: https://stackoverflow.com/a/32611507/4569908
    Given a list of strings, returns the most common substring
    Input: lst = ["wi", "wir▁", "ir▁", "wir", "▁wir▁", "uns", "en", "mu"]
    Output: "wi"
    '''
    subs = Counter()
    for val in lst:
        subs += Counter(val[i:i+j] for i in range(len(val)) for j in range(1, len(val) - i + 1))
    return list(filter(lambda elem: len(elem) > 1, list(zip(*subs.most_common()))[0]))[0]


def max_subarray(arr: list, threshold: int) -> list:
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
    return beg, end, maxval


def aggregate_mappings(unit_maps: defaultdict(Counter), threshold: int, prev_subwords: list=[]) -> dict:
    good_subwords = {}
    for eng_word, deu_maps in unit_maps.items():

        # remove bias in mappings. if there are only 2 mappings, a substring of those will for sure get added
        if len(deu_maps) < 5:
            continue

        # obtain the longest mapping that contains the most common substring
        most_common_unit = most_common_substring(deu_maps)
        for longest in sorted(deu_maps.keys(), key=len, reverse=True):
            if most_common_unit in longest:
                break
        else:
            print("Error. Mapping with most common substring not found")

        # update scores with the scores of the words
        scores = [0 for i in range(len(longest))]
        for word in deu_maps:
            if word in longest:
                # update scores in these indexes
                for i in range(longest.index(word), longest.index(word) + len(word)):
                    scores[i] += float(deu_maps[word])

        # get the characters with the highest scores. maximum subarray of the scores array
        beg, end, count = max_subarray(scores, threshold)
        good_subw = longest[beg:end]
        if (prev_subwords == [] and len(good_subw) > 1) or \
           (prev_subwords != [] and good_subw not in prev_subwords):
            if good_subw in good_subwords:
                good_subwords[good_subw] = max(good_subwords[good_subw], count)
            else:
                good_subwords[good_subw] = count

    # sort good subwords by score, and obtain list with the top-scoring subwords
    good_subwords = sorted(good_subwords, key=good_subwords.get, reverse=True)
    return good_subwords


if __name__ == "__main__":

    for vocab_size in merges:
        unit_maps = parse_mapping(vocab_size)

        subwordfname = join(rootdir, 'data', f'subwords_{vocab_size}.txt')
        # if file already exists, import good_subwords
        if os.path.isfile(subwordfname):
            print("Merging with previous subword list")
            subwordf = codecs.open(subwordfname, 'r', encoding='utf8')
            prev_subwords = [line.strip('\r\n ') for line in subwordf]
        else:
            prev_subwords = []

        # iterate and relax threshold until reaching LIMIT subwords
        threshold = 0.3  # frequency threshold for finding subword units
        LIMIT = int(vocab_size/max_it)
        good_subwords = aggregate_mappings(unit_maps, threshold, prev_subwords)
        while len(good_subwords) < LIMIT:
            threshold *= 0.9
            print(f"Minimum length criteria not met. Trying again with threshold={threshold}")
            good_subwords = aggregate_mappings(unit_maps, threshold, prev_subwords)
        good_subwords = good_subwords[:LIMIT]

        good_subwords = prev_subwords + good_subwords

        # write list of good subwords to file
        print(f"Writing {len(good_subwords)} good subwords")
        out = codecs.open(subwordfname, 'w', encoding='utf8')
        out.write('\n'.join(good_subwords))
