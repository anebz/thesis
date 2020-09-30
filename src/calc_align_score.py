#!/usr/bin/env python3
import os
import sys
import glob
import json
import codecs
import random
import collections
import pandas as pd
import seaborn as sns
from tqdm import tqdm
from os.path import join
import matplotlib.pyplot as plt
from collections import Counter

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

	df = df.sort_values('num_symbols')
	columns = list(df)
	for column, color in zip(columns[1:], colors):
		df.plot(kind='line', x=columns[0], y=column, color=color, ax=ax)

	#plt.ylim(ymax=1, ymin=0)
	plt.savefig(join(scoredir+'.png'))
	return

def calc_align_scores(probs: dict, surs: dict, surs_count: float, i: int=-1) -> pd.DataFrame:

	scores = []
	for num_symbols in merges:
		alfile = join(bpedir, mode, f"{num_symbols}.wgdfa")

		score = [int(num_symbols)]
		score.extend(list(calc_score(alfile, probs, surs, surs_count)))
		scores.append(score)

	df = pd.DataFrame(scores, columns=['num_symbols', 'prec', 'rec', 'f1', 'AER']).round(decimals=3)

	scorename = join(scoredir,  f"{source}_{target}_{mode}")
	print(f"Scores saved into {scorename}")
	df.to_csv(scorename+'.csv', index=False)
	plot_scores(df, scorename)
	return df

# functions for dropout mode
def calc_score_merges(probs, surs, surs_count):
    scorespath = join(scoredir, str(max(params[source]['dropout'], params[target]['dropout'])))
    os.makedirs(scorespath, exist_ok=True)

    ''' currently not doing union and intersection cases
	for merge_type in ['union', 'inter']:
		scores = []
		for num_symbols in merges:
			mergefilepath = join(bpedir, mode, f'{num_symbols}_{merge_type}.wgdfa')
			score = [int(num_symbols)]
			score.extend(list(calc_score(mergefilepath, probs, surs, surs_count)))
			scores.append(score)
			
		df = pd.DataFrame(scores, columns=['num_symbols', 'prec', 'rec', 'f1', 'AER']).round(decimals=3)
		scorename = join(scorespath, f"{source}_{target}_{merge_type}_{mode}")
		
		print(f"Scores saved into {scorename}")
		df.to_csv(scorename+'.csv', index=False)
		plot_scores(df, scorename)
	'''

    # threshold case, iterate all merge_thresholds saved
    for merge_t in merge_threshold:
        scores = []
        for num_symbols in merges:
            mergefilepath = join(bpedir, mode, f'{num_symbols}_thres_{merge_t}.wgdfa')

            score = [int(num_symbols)]
            score.extend(list(calc_score(mergefilepath, probs, surs, surs_count)))
            scores.append(score)

        df = pd.DataFrame(scores, columns=['num_symbols', 'prec', 'rec', 'f1', 'AER']).round(decimals=3)
        scorename = join(scorespath, f"{source}_{target}_{merge_t}_thres_{mode}")
        
        print(f"Scores saved into {scorename}")
        df.to_csv(scorename+'.csv', index=False)
        plot_scores(df, scorename)
    return


if __name__ == "__main__":

	print(f"Calculating alignment scores for: {json.dumps(params, indent=2)}")
	probs, surs, surs_count = load_gold(goldpath)

	if max(params[source]['dropout'], params[target]['dropout']):
		calc_score_merges(probs, surs, surs_count)
	else:
		calc_align_scores(probs, surs, surs_count)
