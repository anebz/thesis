#!/usr/bin/env python3
import argparse
import collections
import os.path
import inspect
import codecs
import glob
import pandas as pd
import matplotlib.pyplot as plt

def load_gold(g_path):
	gold_f = open(g_path, "r")
	pros = {}
	surs = {}
	all_count = 0.
	surs_count = 0.

	for line in gold_f:
		line = line.strip().split("\t")
		line[1] = line[1].split()

		pros[line[0]] = set([x.replace("p", "-") for x in line[1]])
		surs[line[0]] = set([x for x in line[1] if "p" not in x])

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


def plot_scores(df, currentdir, plot_name):

	plt.clf()
	# gca stands for 'get current axis'
	ax = plt.gca()

	colors = ['magenta', 'blue', 'green', 'red']

	# paint horizontal lines to depict baseline
	for baseline_results, color in zip(list(df.iloc[0])[1:], colors):
		plt.axhline(y=baseline_results, color=color, linestyle='dashed')

	df.drop(df.head(1).index, inplace=True)
	df = df.sort_values('num_symbols')
	columns = list(df)
	for column, color in zip(columns[1:], colors):
		df.plot(kind='line', x=columns[0], y=column, color=color, ax=ax)

	plt.grid()
	#plt.ylim(ymax=1, ymin=0)
	plt.savefig(os.path.join(currentdir, plot_name+'.png'))
	return


if __name__ == "__main__":
	'''
	Calculate alignment quality scores based on the gold standard.
	The output contains Precision, Recall, F1, and AER.
	The gold annotated file should be selected by "gold_path".
	The generated alignment file should be selected by "input_path".
	Both gold file and input file are in the FastAlign format with sentence number at the start of line separated with TAB.

	usage: python calc_align_score.py gold_file generated_file

	parser = argparse.ArgumentParser(description="Calculate alignment quality scores based on the gold standard.", epilog="example: python calc_align_score.py gold_path input_path")
	parser.add_argument("gold_path")
	parser.add_argument("input_path")
	args = parser.parse_args()
	'''

	currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
	datapath = os.path.join(currentdir, 'data')

	gold_path = os.path.join(currentdir, 'pbc_utils/data/eng_deu/eng_deu.gold')
	probs, surs, surs_count = load_gold(gold_path)

	scores = []

	# calc score of input
	alfile = os.path.join(datapath, 'fastalign/input.gdfa')
	score = [0]
	score.extend(list(calc_score(alfile, probs, surs, surs_count)))
	scores.append(score)

	# calc score of num_symbols
	os.chdir(datapath + '/fastalign/')
	for alfile in glob.glob('[0-9]*_word.gdfa'):
		num_symbols = alfile.split('/')[-1].split('.')[0].split('_')[0]

		score = [int(num_symbols)]
		score.extend(list(calc_score(alfile, probs, surs, surs_count)))
		scores.append(score)

	df = pd.DataFrame(scores, columns=['num_symbols', 'prec', 'rec', 'f1', 'AER'])
	plot_name = 'scores_deu'
	plot_scores(df, datapath, plot_name)
	df.to_csv(os.path.join(datapath, plot_name+'.csv'), index=False)
