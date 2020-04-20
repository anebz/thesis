#!/usr/bin/env python3
import argparse
import collections
import os.path
import inspect
import codecs
import glob

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

	print("number of gold align sentences:", len(pros), "\n")
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

	output = codecs.open(os.path.join(datapath, 'align_scores.txt'), 'a', encoding='utf-8')

	os.chdir(datapath + '/fastalign/')
	for alfile in glob.glob('*_word.gdfa'):
		input_path = os.path.join(alfile)
		num_symbols = alfile.split('/')[-1].split('.')[0].split('_')[0]

		if not os.path.isfile(input_path):
			print("The input file does not exist:\n", input_path)
			exit()

		y_prec, y_rec, y_f1, aer = calc_score(input_path, probs, surs, surs_count)

		output.write(f"Num symbols: {num_symbols}\tPrec: {y_prec}\tRec: {y_rec}\tF1: {y_f1}\tAER: {aer}\n")

