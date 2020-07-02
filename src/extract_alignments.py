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


def create_parallel_text(sourcepath, targetpath, parallel):

	sourceinput = codecs.open(sourcepath, "r", "utf-8")
	targetinput = codecs.open(targetpath, "r", "utf-8")
	fa_file = codecs.open(parallel, "w", "utf-8")

	for sl, tl in zip(sourceinput, targetinput):
		sl = sl.strip().split("\t")[-1]
		tl = tl.strip().split("\t")[-1]

		fa_file.write(sl + " ||| " + tl + "\n")
	fa_file.close()
	return


def extract_alignments(i=-1, input_mode=False):

	for num_symbols in all_symbols:

		if input_mode:
			print(f"Alignments for input files")
			sourcepath = inputpath[source]
			targetpath = inputpath[target]
			outpath = join(bpedir, "fastalign/input")
		else:
			print(f"Alignments for {num_symbols} symbols")
			if target_bpe:
				sourcepath = inputpath[source]
			else:
				sourcepath = join(bpedir, 'segmentations', 
							source+"_"+str(num_symbols)+('_'+str(i) if dropout else '')+".bpe")
			
			if source_bpe:
				targetpath = inputpath[target]
			else:
				targetpath = join(bpedir, 'segmentations', 
							target+"_"+str(num_symbols)+('_'+str(i) if dropout else '')+".bpe")

			outpath = join(bpedir, "fastalign", str(num_symbols) +
						('_'+str(i) if i != -1 else '') +
						('_deu' if target_bpe else '')
					)
		
		parallel = outpath + ".txt"
		create_parallel_text(sourcepath, targetpath, parallel)

		if mode == "fastalign":
			os.system(f"{fastalign_path} -i {parallel} -v -d -o > {outpath}.fwd")
			os.system(f"{fastalign_path} -i {parallel} -v -d -o -r > {outpath}.rev")
		elif mode == "eflomal":
			os.system(f"cd {eflomal_path}; python align.py -i {parallel} --model 3 -f {outpath}.fwd -r {outpath}.rev")

		os.system(f"{atools_path} -i {outpath}.fwd -j {outpath}.rev -c grow-diag-final-and > {outpath}_unnum.gdfa")
		add_numbers(outpath + "_unnum.gdfa", outpath + ".gdfa")
		os.system(f"rm {outpath}_unnum.gdfa")
		os.system(f"rm {outpath}.fwd")
		os.system(f"rm {outpath}.rev")
		os.system(f"rm {outpath}.txt")

		if input_mode:
			break

		# map alignment from subword to word
		bpes = load_and_map_segmentations(num_symbols, i)

		argsalign = codecs.open(outpath+'.gdfa', encoding='utf-8')
		all_word_aligns = bpe_word_align(bpes, argsalign)
		os.system("rm {}.gdfa".format(outpath))

		argsoutput = codecs.open(outpath+'.wgdfa', 'w', encoding='utf-8')
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
