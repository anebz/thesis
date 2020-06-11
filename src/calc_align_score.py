#!/usr/bin/env python3
import os
from os.path import join
import sys
import glob
import random
import collections
import pandas as pd
import matplotlib.pyplot as plt

# import global variables from settings.py
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from settings import *


def load_gold(g_path):

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


def calc_score(input_path, probs, surs, surs_count):

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


def get_baseline_score(probs, surs, surs_count):

	alfile = join(bpedir, 'fastalign/input.wgdfa')

	scores = []
	score = [0]
	score.extend(list(calc_score(alfile, probs, surs, surs_count)))
	scores.append(score)
	baseline_df = pd.DataFrame(scores, columns=['num_symbols', 'prec', 'rec', 'f1', 'AER']).round(decimals=3)
	return baseline_df


def plot_scores(df, baseline_df, scoredir):

	plt.clf()
	# gca stands for 'get current axis'
	ax = plt.gca()

	colors = ['magenta', 'blue', 'green', 'red']

	df = df.sort_values('num_symbols')
	columns = list(df)
	for column, color in zip(columns[1:], colors):
		df.plot(kind='line', x=columns[0], y=column, color=color, ax=ax)

	if dropout:
		baseline_df = baseline_df.sort_values('num_symbols')
		columns = list(baseline_df)
		for column, color in zip(columns[1:], colors):
			baseline_df.plot(kind='line', x=columns[0], y=column,
							 color=color, ax=ax, legend=False, linestyle='dashed')
	else:
		for baseline_results, color in zip(list(baseline_df.iloc[0][1:]), colors):
			plt.axhline(y=baseline_results, color=color, linestyle='dashed')

	plt.grid()
	#plt.ylim(ymax=1, ymin=0)
	plt.savefig(join(scoredir+'.png'))
	return


def calc_align_scores(probs, surs, surs_count, baseline_df, i=-1):

	scores = []
	# calc score of num_symbols
	os.chdir(join(bpedir, 'fastalign'))
	for alfile in glob.glob('[0-9]*'+
							('_'+str(i) if dropout else '')+
							('_'+source if source_bpe else '')+
							('_'+target if target_bpe else '')+'.wgdfa'):
		if (not target_bpe and '_'+target in alfile) or (not source_bpe and '_'+source in alfile):
			continue
		num_symbols = alfile.split('/')[-1].split('.')[0].split('_')[0]

		score = [int(num_symbols)]
		score.extend(list(calc_score(alfile, probs, surs, surs_count)))
		scores.append(score)

	df = pd.DataFrame(scores, columns=['num_symbols', 'prec', 'rec', 'f1', 'AER']).round(decimals=3)

	scorename = join(scoredir, 'scores')
	if dropout:
		scorename += '_' + str(i)
	elif not (target_bpe or source_bpe):
		scorename += '_' + source + '_' + target
	if not space:
		scorename += '_ns'
	if target_bpe:
		scorename += '_' + target
	if source_bpe:
		scorename += '_' + source

	if not dropout:
		print(f"Scores saved into {scorename}")
		df.to_csv(scorename+'.csv', index=False)
		plot_scores(df, baseline_df, scorename)
	return df


def avg_scores(baseline_df, score_dfs):

	for avg in avgs:

		# get random i indexes
		random_idx = set()
		while len(random_idx) < avg:
			random_idx.add(random.randrange(10))
		
		df = pd.DataFrame()
		for rd_idx in list(random_idx):

			# first step of the iteration, just get the whole dataframe
			if df.empty:
				df = score_dfs[rd_idx]
				continue

			for col in list(score_dfs[rd_idx])[1:]:
				df[col] += score_dfs[rd_idx][col]

		# divide all by \# elements added, to get average
		for col in list(df)[1:]:
			df[col] = df[col].apply(lambda x: x/avg)

		scoredir = join(scoredir, 'scores_avg_'+str(avg)+('_'+source if source_bpe else '')+('_'+target if target_bpe else ''))
		print(f"Scores saved into {scoredir}")
		df.round(decimals=3).to_csv(os.path.join(scoredir+'.csv'), index=False)
		plot_scores(df, baseline_df, join(scoredir))

	return


if __name__ == "__main__":
	'''
	Calculate alignment quality scores based on the gold standard.
	The output contains Precision, Recall, F1, and AER.
	The gold annotated file should be selected by "gold_path".
	The generated alignment file should be selected by "input_path".
	Both gold file and input file are in the FastAlign format with sentence number at the start of line separated with TAB.
	'''

	print(f"Calculating alignment scores for source={source} and target={target}, dropout={dropout}, source_bpe={source_bpe}, target_bpe={target_bpe}.")

	probs, surs, surs_count = load_gold(goldpath)

	# dropout case: take normal BPE scores as baseline. if normal case, take gold standard
	if dropout or not space:
		baseline_df = pd.read_csv(join(rootdir, 'reports/scores_normal_bpe', 'scores_'+source+'_'+target+'.csv'))
	else:
		baseline_df = get_baseline_score(probs, surs, surs_count)

	if dropout > 0:
		score_dfs = [calc_align_scores(probs, surs, surs_count, baseline_df, i) for i in range(dropout_repetitions)]
		avg_scores(baseline_df, score_dfs)
	else:
		calc_align_scores(probs, surs, surs_count, baseline_df)
