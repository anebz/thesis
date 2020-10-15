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
        "we": ["w", "wi", "ir", "r_", "wi", "wir_", ...],
        "do": ["i", "n", "ch", ...], ...
    ]
    Output: {
        "we": {"wi": "0.1833", "wir▁": "0.1497", ...},
        "do": {"i": "0.0715", "n": "0.0709", "ch": "0.0582", ...}, ...
    }
    '''
    
    for key, value in unit_maps.items():
        c = Counter(value)
        unit_maps[key] = {i: f"{c[i]/len(value):.4f}" for i, _ in c.most_common(15)}
    return unit_maps


if __name__ == "__main__":

    symb = merges[0]
    unit_maps = defaultdict(list)
    for it in range(dropout_samples):
        alfile = codecs.open(join(bpedir, mode, f'{symb}_{it}.gdfa'), 'r', 'utf-8')
        sourcefile = codecs.open(inputpath[source], 'r', 'utf-8')
        targetfile = codecs.open(join(bpedir, 'segmentations', f'{target}_{symb}_{it}.bpe'), 'r', 'utf-8')

        for al_line, source_line, target_line in zip(alfile, sourcefile, targetfile):
            almaps = parse_alignment(al_line)
            source_line, target_line = parse_segmentations(source_line, target_line)

            # obtain segmentation mappings and save to unit_maps
            for i, unit_source in enumerate(source_line):
                unit_source = unit_source.replace(word_sep, '')
                if almaps[i]:
                    unit_maps[unit_source].extend(list(map(target_line.__getitem__, almaps[i])))

    unit_maps = parse_mapping(unit_maps)

    with open(join(bpedir, 'mapping.json'), 'w', encoding='utf8') as out:
        json.dump(unit_maps, out, indent=2, ensure_ascii=False)
