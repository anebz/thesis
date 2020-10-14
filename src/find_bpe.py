#!/usr/bin/env python3
import sys
import codecs
from tqdm import tqdm
from os.path import join
from collections import defaultdict

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
    return source_line.strip('\n').split(), target_line.strip('\n').split()


if __name__ == "__main__":

    symb = merges[0]
    unit_maps = defaultdict(list)
    for it in range(dropout_samples):
        alfile = codecs.open(join(bpedir, mode, f'{symb}_{it}.gdfa'), 'r', 'utf-8')
        segm_source = codecs.open(join(bpedir, 'segmentations', f'{source}_{symb}.bpe'), 'r', 'utf-8')
        segm_target = codecs.open(join(bpedir, 'segmentations', f'{target}_{symb}_{it}.bpe'), 'r', 'utf-8')

        for al_line, source_line, target_line in zip(alfile, segm_source, segm_target):
            almaps = parse_alignment(al_line)
            source_line, target_line = parse_segmentations(source_line, target_line)

            # obtain segmentation mappings and save to unit_maps
            for i, unit_source in enumerate(source_line):
                if almaps[i]:
                    unit_maps[unit_source].extend(list(map(target_line.__getitem__, almaps[i])))
