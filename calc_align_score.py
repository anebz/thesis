#!/usr/bin/env python3
import collections
import os
from os.path import join
import codecs
import glob
import pandas as pd
import matplotlib.pyplot as plt

# import global variables from lib/__init__.py
from lib import *


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


def calc_align_scores(i=-1):

	gold_path = join(datadir, 'input/eng_deu.gold')
	probs, surs, surs_count = load_gold(gold_path)

	# dropout case: take normal BPE scores as baseline. if normal case, take gold standard
	if dropout:
		baseline_df = pd.read_csv(join(datadir, 'normal_bpe/scores/scores_'+source+'_'+target+'.csv'))
	else:
		baseline_df = get_baseline_score(probs, surs, surs_count)
		
	scores = []
	# calc score of num_symbols
	os.chdir(join(bpedir, 'fastalign'))
	for alfile in glob.glob('[0-9]*_'+('deu' if german_bpe else '')+(str(i) if dropout else '')+'.wgdfa'):
		num_symbols = alfile.split('/')[-1].split('.')[0].split('_')[0]

		score = [int(num_symbols)]
		score.extend(list(calc_score(alfile, probs, surs, surs_count)))
		scores.append(score)

	df = pd.DataFrame(scores, columns=['num_symbols', 'prec', 'rec', 'f1', 'AER']).round(decimals=3)

	scoredir = join(bpedir, 'scores', 'scores' + ('_deu' if german_bpe else ''))
	if dropout:
		scoredir += '_' + str(i)
	elif not german_bpe:
		scoredir += '_' + source + '_' + target

	print(f"Scores saved into {scoredir}")

	df.to_csv(scoredir+'.csv', index=False)
	plot_scores(df, baseline_df, scoredir)
	return


if __name__ == "__main__":
	'''
	Calculate alignment quality scores based on the gold standard.
	The output contains Precision, Recall, F1, and AER.
	The gold annotated file should be selected by "gold_path".
	The generated alignment file should be selected by "input_path".
	Both gold file and input file are in the FastAlign format with sentence number at the start of line separated with TAB.
	'''

	if dropout > 0:
        # create `dropout_repetitions` segmentations, to aggregate later
		for i in range(dropout_repetitions):
			print(f"Iteration {i+1}")
			calc_align_scores(i)
	else:
		calc_align_scores()
