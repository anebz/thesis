#!/usr/bin/env python3
import os
import sys
import glob
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
	pros = {}
	surs = {}
	all_count = 0.
	surs_count = 0.

	for line in gold_f:
		line = line.strip().split("\t")
		line[1] = line[1].split()

		pros[line[0]] = set()
		surs[line[0]] = set()

		for al in line[1]:
			# swap eng-deu alignments when source is german
			if source == 'deu':
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

	#print("number of gold align sentences:", len(pros), "\n")
	return pros, surs, surs_count


def calc_score(input_path: str, probs: dict, surs: dict, surs_count: int) -> (float, float, float, float):

	total_hit = 0.
	p_hit = 0.
	s_hit = 0.
	target_f = open(input_path, "r")

	for line in target_f:
		line = line.strip().split("\t")

		if line[0] not in probs: continue
		if len(line) < 2: continue

		line[1] = line[1].split()

		# swap alignments in the swapped language case
		if source == 'deu':
			line[1] = [al.split('-')[1] + '-' + al.split('-')[0] for al in line[1]]

		for pair in line[1]:
			if pair in probs[line[0]]:
				p_hit += 1
			if pair in surs[line[0]]:
				s_hit += 1

			total_hit += 1

	target_f.close()

	y_prec = round(p_hit / max(total_hit, 1.), 3)
	y_rec = round(s_hit / max(surs_count, 1.), 3)
	y_f1 = round(2. * y_prec * y_rec / max((y_prec + y_rec), 0.01), 3)
	aer = round(1 - (s_hit + p_hit) / (total_hit + surs_count), 3)

	return y_prec, y_rec, y_f1, aer


def get_baseline_score(probs: dict, surs: dict, surs_count: float) -> pd.DataFrame:

	alfile = join(bpedir, mode, f'input_{source}_{target}.gdfa')

	score = [0]
	score.extend(list(calc_score(alfile, probs, surs, surs_count)))
	baseline_df = pd.DataFrame([score], columns=['num_symbols', 'prec', 'rec', 'f1', 'AER']).round(decimals=3)
	return baseline_df


def plot_scores(df: pd.DataFrame, baseline_df: pd.DataFrame, scoredir: str):

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

	if dropout:
		if not baseline_df.empty:
			baseline_df = baseline_df.sort_values('num_symbols')
			columns = list(baseline_df)
			for column, color in zip(columns[1:], colors):
				baseline_df.plot(kind='line', x=columns[0], y=column,
									color=color, ax=ax, legend=False, linestyle='dashed')
	else:
		for baseline_results, color in zip(list(baseline_df.iloc[0][1:]), colors):
			plt.axhline(y=baseline_results, color=color, linestyle='dashed')

	#plt.ylim(ymax=1, ymin=0)
	plt.savefig(join(scoredir+'.png'))
	return

def calc_align_scores(probs: dict, surs: dict, surs_count: float, baseline_df: pd.DataFrame, i: int =-1) -> pd.DataFrame:

	scores = []
	for num_symbols in merges:
		alfile = join(bpedir, mode, 
			f"{num_symbols}{'_'+str(i) if dropout else ''}{'_'+source if source_bpe else ''}{'_'+target if target_bpe else ''}.wgdfa")

		if (not target_bpe and '_'+target in alfile) or (not source_bpe and '_'+source in alfile):
			continue

		score = [int(num_symbols)]
		score.extend(list(calc_score(alfile, probs, surs, surs_count)))
		scores.append(score)

	df = pd.DataFrame(scores, columns=['num_symbols', 'prec', 'rec', 'f1', 'AER']).round(decimals=3)

	scorename = scoredir + '/' + source + '_' + target
	if not space:
		scorename += '_ns'
	if target_bpe:
		scorename += '_' + target
	if source_bpe:
		scorename += '_' + source
	scorename += '_' + mode

	if not dropout:
		print(f"Scores saved into {scorename}")
		df.to_csv(scorename+'.csv', index=False)
		plot_scores(df, baseline_df, scorename)
	return df

# functions for dropout mode
def calc_score_merges(probs, surs, surs_count, baseline_df):
    scorespath = join(scoredir, 'space' if space else 'no space', str(dropout))
    os.makedirs(scorespath, exist_ok=True)
    for merge_type in ['union', 'inter']:
        scores = []
        for num_symbols in merges:
            mergefilepath = join(bpedir, mode, f'{num_symbols}_{merge_type}.wgdfa')

            score = [int(num_symbols)]
            score.extend(list(calc_score(mergefilepath, probs, surs, surs_count)))
            scores.append(score)

       	df = pd.DataFrame(scores, columns=['num_symbols', 'prec', 'rec', 'f1', 'AER']).round(decimals=3)
        scorename = join(scorespath, f"{source}_{target}_{''if space else 'ns_'}{merge_type}_{mode}{'_'+source if source_bpe else ''}{'_'+target if target_bpe else ''}")

        print(f"Scores saved into {scorename}")
        df.to_csv(scorename+'.csv', index=False)
        plot_scores(df, baseline_df, scorename)

    # threshold case, iterate all merge_thresholds saved
    for merge_t in merge_threshold:
        scores = []
        for num_symbols in merges:
            mergefilepath = join(bpedir, mode, f'{num_symbols}_thres_{merge_t}.wgdfa')

            score = [int(num_symbols)]
            score.extend(list(calc_score(mergefilepath, probs, surs, surs_count)))
            scores.append(score)

        df = pd.DataFrame(scores, columns=['num_symbols', 'prec', 'rec', 'f1', 'AER']).round(decimals=3)
        scorename = join(scorespath, f"{source}_{target}_{'' if space else 'ns_'}{merge_t}_thres_{mode}{'_'+source if source_bpe else ''}{'_'+target if target_bpe else ''}")
        
        print(f"Scores saved into {scorename}")
        df.to_csv(scorename+'.csv', index=False)
        plot_scores(df, baseline_df, scorename)
    return


if __name__ == "__main__":

	print(f"Calculating alignment scores for source={source} and target={target}, source_bpe={source_bpe}, target_bpe={target_bpe}.")
	probs, surs, surs_count = load_gold(goldpath)

	if dropout:
		try:
			baseline_df = pd.read_csv(join(baselinedir, f"{source}_{target}{'' if space else '_ns'}{'_'+source if source_bpe else ''}{'_'+target if target_bpe else ''}_{mode}.csv"))
		except:
			print("Baseline not available")
			baseline_df = pd.DataFrame()
		calc_score_merges(probs, surs, surs_count, baseline_df)
	else:
		# no space case: take normal BPE scores as baseline. if normal case, take gold standard
		if not space:
			baseline_df = pd.read_csv(join(rootdir, 'reports/scores_normal_bpe', f'{source}_{target}_{mode}.csv'))
		else:
			baseline_df = get_baseline_score(probs, surs, surs_count)
		calc_align_scores(probs, surs, surs_count, baseline_df)
