#!/usr/bin/env python3
from os.path import join
import os
import sys
import codecs

# import global variables from settings.py
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from settings import *
from subword_word import *


def create_parallel_text(sourcepath, targetpath, outpath):

	sourceinput = codecs.open(sourcepath, "r", "utf-8")
	targetinput = codecs.open(targetpath, "r", "utf-8")
	fa_file = codecs.open(outpath + '.txt', "w", "utf-8")

	for sl, tl in zip(sourceinput, targetinput):
		sl = sl.strip().split("\t")[-1]
		tl = tl.strip().split("\t")[-1]
		fa_file.write(f"{sl} ||| {tl}\n")
	fa_file.close()
	return

def create_fwd_rev_files(outpath):
	if mode == "fastalign":
		os.system(f"{fastalign_path} -i {outpath}.txt -v -d -o > {outpath}.fwd")
		os.system(f"{fastalign_path} -i {outpath}.txt -v -d -o -r > {outpath}.rev")
	elif mode == "eflomal":
		os.system(f"cd {eflomal_path}; python align.py -i {outpath}.txt --model 3 -f {outpath}.fwd -r {outpath}.rev")
	return


def create_gdfa_file(outpath):
	# create gdfa file from .fwd and .rev
	os.system(f"{atools_path} -i {outpath}.fwd -j {outpath}.rev -c grow-diag-final-and > {outpath}_unnum.gdfa")

	# parse _unnum.gdfa to .gdfa with "\t" separator
	with codecs.open(f"{outpath}_unnum.gdfa", "r", "utf-8") as fi, codecs.open(f"{outpath}.gdfa", "w", "utf-8") as fo:
		for i, line in enumerate(fi):
			fo.write(f"{i}\t{line.strip()}\n")

	# delete unnecessary files
	os.system(f"rm {outpath}_unnum.gdfa; rm {outpath}.fwd; rm {outpath}.rev; rm {outpath}.txt")
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

		create_parallel_text(sourcepath, targetpath, outpath)
		create_fwd_rev_files(outpath)
		create_gdfa_file(outpath)

		if input_mode:
			break

		# map alignment from subword to word
		bpes = load_and_map_segmentations(num_symbols, i)

		argsalign = codecs.open(outpath+'.gdfa', encoding='utf-8')
		all_word_aligns = bpe_word_align(bpes, argsalign)
		os.system(f"rm {outpath}.gdfa")

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
