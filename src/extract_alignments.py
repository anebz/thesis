#!/usr/bin/env python3
from os.path import join
import os
import sys
import codecs
import argparse

# import global variables from settings.py
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from settings import *
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
			s = inputpath[source]
			t = inputpath[target]
			o = join(bpedir, "fastalign/input")

		else:
			print(f"Alignments for {num_symbols} symbols")
			if target_bpe:
				s = inputpath[source]
			else:
				s = join(bpedir, 'segmentations', source+"_"+str(num_symbols)+('_'+str(i) if dropout else '')+".bpe")
			
			if source_bpe:
				t = inputpath[target]
			else:
				t = join(bpedir, 'segmentations', target+"_"+str(num_symbols)+('_'+str(i) if dropout else '')+".bpe")

			o = join(bpedir, "fastalign",
						str(num_symbols) +
						('_'+str(i) if i != -1 else '') +
						('_deu' if target_bpe else '')
					)

		# create parallel text
		p = o + ".txt"

		fa_file = codecs.open(p, "w", "utf-8")
		fsrc = codecs.open(s, "r", "utf-8")
		ftrg = codecs.open(t, "r", "utf-8")

		for sl, tl in zip(fsrc, ftrg):
			sl = sl.strip().split("\t")[-1]
			tl = tl.strip().split("\t")[-1]

			fa_file.write(sl + " ||| " + tl + "\n")
		fa_file.close()

		if mode == "fastalign":
			os.system(f"{fastalign_path} -i {p} -v -d -o > {o}.fwd")
			os.system(f"{fastalign_path} -i {p} -v -d -o -r > {o}.rev")
		elif mode == "eflomal":
			os.system(f"cd {eflomal_path}; python align.py -i {p} --model 3 -f {o}.fwd -r {o}.rev")

		os.system(f"{atools_path} -i {o}.fwd -j {o}.rev -c grow-diag-final-and > {o}_unnum.gdfa")
		add_numbers(o + "_unnum.gdfa", o + ".gdfa")
		os.system(f"rm {o}_unnum.gdfa")
		os.system(f"rm {o}.fwd")
		os.system(f"rm {o}.rev")
		os.system(f"rm {o}.txt")

		if input_mode:
			break

		# map alignment from subword to word
		bpes = load_and_map_segmentations(num_symbols, i)

		argsalign = codecs.open(o+'.gdfa', encoding='utf-8')
		all_word_aligns = bpe_word_align(bpes, argsalign)
		os.system("rm {}.gdfa".format(o))

		argsoutput = codecs.open(o+'.wgdfa', 'w', encoding='utf-8')
		argsoutput.write(all_word_aligns)

		print("\n\n")
	return

if __name__ == "__main__":
	'''
	Extract alignments with different models and store in files.
	The output_file is set by "-o" and is the path and name of the output file without extension.
	The alignment model is set by "-m". The options are "fast" for Fastalign and "eflomal".
	Input files can either be two separate source and target files, or a single parallel file in Fastalign format.

	usage 1: ./extract_alignments.py -s file1 -t file2 -o output_file
	usage 2: ./extract_alignments.py -p parallel_file -o output_file
	'''

	print(f"Extracting alignments for source={source} and target={target}, dropout={dropout}, source_bpe={source_bpe}, target_bpe={target_bpe}.")

	os.makedirs(join(bpedir, 'fastalign'), exist_ok=True)
	if not os.path.isfile(join(bpedir, 'fastalign/input.wgdfa')):
		extract_alignments(input_mode=True)

	if dropout > 0:
		# create `dropout_samples` segmentations, to aggregate later
		for i in range(dropout_samples):
			print(f"Iteration {i+1}")
			extract_alignments(i)
			print("\n\n\n\n")
	else:
		extract_alignments()
