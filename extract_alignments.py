#!/usr/bin/env python3
import codecs
import argparse
from os.path import join
import os

# import global variables from lib/__init__.py
from lib import *
from subword_word import *

def add_numbers(input_file, output_file, start=0, max_num=-1):
	with codecs.open(input_file, "r", "utf-8") as fi, codecs.open(output_file, "w", "utf-8") as fo:
		count = start
		for l in fi:
			fo.write(str(count) + "\t" + l.strip() + "\n")
			count += 1
			if max_num > 0 and count >= max_num:
				break


def extract_alignments(i=-1, input_mode=False):

	for num_symbols in all_symbols:

		if input_mode:
			print(f"Alignments for input files")
			s = join(datapath, "input/eng_with_10k.txt")
			t = join(datapath, "input/deu_with_10k.txt")
			o = join(bpepath, "fastalign/input")

		else:
			print(f"Alignments for {num_symbols} symbols")
			s = join(bpepath, 'segmentations', "eng_"+str(num_symbols)+('_'+str(i) if i != -1 else '')+".bpe")
			t = join(bpepath, 'segmentations', "deu_"+str(num_symbols)+('_'+str(i) if i != -1 else '')+".bpe")
			o = join(bpepath, "fastalign", str(num_symbols)+('_'+str(i) if i != -1 else ''))

		p = ""
		m = "fast"

		# create parallel text
		if p == "" and m == "fast":
			p = o + ".txt"

			fa_file = codecs.open(p, "w", "utf-8")
			fsrc = codecs.open(s, "r", "utf-8")
			ftrg = codecs.open(t, "r", "utf-8")

			for sl, tl in zip(fsrc, ftrg):
				sl = sl.strip().split("\t")
				tl = tl.strip().split("\t")

				if len(sl) == 2 and len(tl) == 2:
					sl = sl[1]
					tl = tl[1]
				else:
					sl = sl[0]
					tl = tl[0]

				fa_file.write(sl + " ||| " + tl + "\n")
			fa_file.close()

		if m == "fast":
			os.system("{} -i {} -v -d -o > {}.fwd".format(fastalign_path, p, o))
			os.system("{} -i {} -v -d -o -r > {}.rev".format(fastalign_path, p, o))
		elif m == "eflomal":
			os.system(eflomal_path + "align.py -i {0} --model 3 -f {1}.fwd -r {1}.rev".format(p, o))

		os.system("{0} -i {1}.fwd -j {1}.rev -c grow-diag-final-and > {1}_unnum.gdfa".format(atools_path, o))
		add_numbers(o + "_unnum.gdfa", o + ".gdfa")
		os.system("rm {}_unnum.gdfa".format(o))

		'''
		with open(o + ".fwd", "r") as f1, open(o + ".rev", "r") as f2, open(o + ".inter", "w") as fo:
			count = 0
			for l1, l2 in zip(f1, f2):
				l1 = set(l1.strip().split())
				l2 = set(l2.strip().split())
				fo.write(str(count) + "\t" + " ".join(sorted([x for x in l1 & l2])) + "\n")
				count += 1
		'''

		if input_mode:
			break

		# map alignment from subword to word
		german_bpe = False
		bpes = load_and_map_segmentations(num_symbols, i, german_bpe)

		argsalign = codecs.open(join(bpepath, o+'.gdfa'), encoding='utf-8')
		all_word_aligns = bpe_word_align(bpes, argsalign)

		argsoutput = codecs.open(o+'_word.gdfa', 'w', encoding='utf-8')
		argsoutput.write(all_word_aligns)

		print("\n\n\n\n")
	return

if __name__ == "__main__":
	'''
	Extract alignments with different models and store in files.
	The output_file is set by "-o" and is the path and name of the output file without extension.
	The alignment model is set by "-m". The options are "fast" for Fastalign and "eflomal".
	Input files can either be two separate source and target files, or a single parallel file in Fastalign format.

	usage 1: ./extract_alignments.py -s file1 -t file2 -o output_file
	usage 2: ./extract_alignments.py -p parallel_file -o output_file

	example: ./extract_alignments.py -p data/eng_deu.txt -m fast -o alignments/eng_deu
	'''

	eflomal_path = "/mounts/Users/student/masoud/tools/eflomal-master/"

	# ubuntu
	fastalign_path = join(rootdir, "tools/fast_align/build/fast_align")
	atools_path = join(rootdir, "tools/fast_align/build/atools")

	if not os.path.isfile(join(bpepath, 'fastalign/input.gdfa')):
		extract_alignments(input_mode=True)

	if dropout > 0:
		# create `dropout_repetitions` segmentations, to aggregate later
		for i in range(dropout_repetitions):
			print(f"Iteration {i+1}")
			extract_alignments(i)
			print("\n\n\n\n")
	else:
		extract_alignments()
