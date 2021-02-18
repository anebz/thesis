#!/usr/bin/env python3
import os
import sys
import json
import codecs
import pandas as pd
from tqdm import tqdm
import seaborn as sns
from os.path import join
from collections import Counter
import matplotlib.pyplot as plt

# import global variables from settings.py
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from settings import *


def load_gold(g_path: str) -> (dict, dict, int):
	gold_f = open(g_path, "r")
	pros, surs = {}, {}
	all_count, surs_count = 0., 0.

	for line in gold_f:
		line = line.strip().split("\t")
		line[1] = line[1].split()
		pros[line[0]], surs[line[0]] = set(), set()

		for al in line[1]:
			# swap eng-deu alignments when source is german
			if source != 'eng':
				second, first = al.replace('p', '-').split('-')
				pros[line[0]].add(first + '-' + second)
				if 'p' not in al:
					surs[line[0]].add(first + '-' + second)
			else:
				pros[line[0]].add(al.replace('p', '-'))
				if 'p' not in al:
					surs[line[0]].add(al)

		all_count += len(pros[line[0]])
		surs_count += len(surs[line[0]])

	return pros, surs, surs_count


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


def load_and_map_segmentations(vocab_size: str, i: int = -1) -> dict:
    bpes = {}

    for lang in [source, target]:
        if params[lang]['bpe']:
            segmentpath = join(
                bpedir, 'segmentations', f"{lang}_{vocab_size}{'_'+str(i) if params[lang]['dropout'] > 0 else ''}.bpe")
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


def merge_dropout_alignments():
	thres_merge = {}
	for vocab_size in tqdm(merges, desc=f"merging dropout align files"):
		thres_merge[vocab_size] = []
		for i in range(dropout_samples):

			# map alignment from subword to word
			bpes = load_and_map_segmentations(vocab_size, i)
			outpath = codecs.open(join(bpedir, mode, f"{vocab_size}{'_'+str(i) if i != -1 else ''}.gdfa"), encoding='utf-8')
			all_word_aligns = bpe_word_align(bpes, outpath)

			# merge dropout alignments
			for j, line in enumerate(all_word_aligns):
				al = frozenset(line.strip().split("\t")[1].split())

				# at the first iteration, just append the alignment
				if i == 0:
					thres_merge[vocab_size].append(Counter(al))
					continue
				thres_merge[vocab_size][j] += Counter(al)

		# write to output
		os.chdir(join(bpedir, mode))
		thresfiles = {merge_t: codecs.open(f'{vocab_size}_thres_{merge_t}.wgdfa', 'w') for merge_t in merge_threshold}

		for i in range(len(thres_merge[vocab_size])):
			# get alignments more common than the merge_threshold %
			for merge_t in merge_threshold:
				common_aligns = [k for k in thres_merge[vocab_size][i]
								if thres_merge[vocab_size][i][k] > merge_t * dropout_samples]
				thresfiles[merge_t].write(f"{i}\t{' '.join(common_aligns)}\n")
	return


def calc_score(input_path: str, probs: dict, surs: dict, surs_count: int) -> (float, float, float, float):
	total_hit, p_hit, s_hit = 0., 0., 0.

	with open(input_path, "r") as target_f:
		for line in target_f:
			line = line.strip().split("\t")

			if line[0] not in probs: continue
			if len(line) < 2: continue

			line[1] = line[1].split()
			# swap alignments in the swapped language case
			if source != 'eng':
				line[1] = [al.split('-')[1] + '-' + al.split('-')[0] for al in line[1]]

			for pair in line[1]:
				if pair in probs[line[0]]:
					p_hit += 1
				if pair in surs[line[0]]:
					s_hit += 1
				total_hit += 1

	y_prec = round(p_hit / max(total_hit, 1.), 3)
	y_rec = round(s_hit / max(surs_count, 1.), 3)
	y_f1 = round(2. * y_prec * y_rec / max((y_prec + y_rec), 0.01), 3)
	aer = round(1 - (s_hit + p_hit) / (total_hit + surs_count), 3)

	return y_prec, y_rec, y_f1, aer


def plot_scores(df: pd.DataFrame, scoredir: str):

	# Use plot styling from seaborn.
	sns.set(style='darkgrid')

	# Increase the plot size and font size.
	sns.set(font_scale=1.5)
	plt.rcParams["figure.figsize"] = (12, 6)

	plt.clf()
	ax = plt.gca() # gca stands for 'get current axis'

	colors = ['magenta', 'tab:blue', 'tab:green', 'tab:red']

	df = df.sort_values('vocab_size')
	columns = list(df)
	for column, color in zip(columns[1:], colors):
		df.plot(kind='line', x=columns[0], y=column, color=color, ax=ax)

	#plt.ylim(ymax=1, ymin=0)
	plt.savefig(join(scoredir+'.png'))
	return

def calc_align_scores(probs: dict, surs: dict, surs_count: float, i: int=-1) -> pd.DataFrame:

	scores = []
	for vocab_size in merges:
		alfile = join(bpedir, mode, f"{vocab_size}_{i}.wgdfa")

		score = [int(vocab_size)]
		score.extend(list(calc_score(alfile, probs, surs, surs_count)))
		scores.append(score)

	df = pd.DataFrame(scores, columns=['vocab_size', 'prec', 'rec', 'f1', 'AER']).round(decimals=3)

	scorename = join(scoredir,  f"{source}_{target}_{mode}")
	print(f"Scores saved into {scorename}")
	df.to_csv(scorename+'.csv', index=False)
	#plot_scores(df, scorename)
	return df

# functions for dropout mode
def calc_score_merges(probs, surs, surs_count):
    scorespath = join(scoredir, str(max(params[source]['dropout'], params[target]['dropout'])))
    os.makedirs(scorespath, exist_ok=True)

    ''' currently not doing union and intersection cases
	for merge_type in ['union', 'inter']:
		scores = []
		for vocab_size in merges:
			mergefilepath = join(bpedir, mode, f'{vocab_size}_{merge_type}.wgdfa')
			score = [int(vocab_size)]
			score.extend(list(calc_score(mergefilepath, probs, surs, surs_count)))
			scores.append(score)
			
		df = pd.DataFrame(scores, columns=['vocab_size', 'prec', 'rec', 'f1', 'AER']).round(decimals=3)
		scorename = join(scorespath, f"{source}_{target}_{merge_type}_{mode}")
		
		print(f"Scores saved into {scorename}")
		df.to_csv(scorename+'.csv', index=False)
		#plot_scores(df, scorename)
	'''

    # threshold case, iterate all merge_thresholds saved
    for merge_t in merge_threshold:
        scores = []
        for vocab_size in merges:
            mergefilepath = join(bpedir, mode, f'{vocab_size}_thres_{merge_t}.wgdfa')

            score = [int(vocab_size)]
            score.extend(list(calc_score(mergefilepath, probs, surs, surs_count)))
            scores.append(score)

        df = pd.DataFrame(scores, columns=['vocab_size', 'prec', 'rec', 'f1', 'AER']).round(decimals=3)
        scorename = join(scorespath, f"{source}_{target}_{merge_t}_thres_{mode}")
        
        print(f"Scores saved into {scorename}")
        df.to_csv(scorename+'.csv', index=False)
        #plot_scores(df, scorename)
    return


if __name__ == "__main__":

	merge_dropout_alignments()

	print(f"Calculating alignment scores for: {json.dumps(params, indent=2)}")
	probs, surs, surs_count = load_gold(join(inputdir, source+'_'+target+'.gold'))

	if max(params[source]['dropout'], params[target]['dropout']):
		calc_score_merges(probs, surs, surs_count)
	else:
		calc_align_scores(probs, surs, surs_count, 0)
