#!/usr/bin/env python3
import os
import sys
import time
import json
import codecs
from tqdm import tqdm
from os.path import join
from datetime import timedelta
from collections import Counter

# import global variables from settings.py
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from settings import *
from subword_word import *


def create_parallel_text(sourcepath: str, targetpath: str, outpath: str):
	sourceinput = codecs.open(sourcepath, "r", "utf-8")
	targetinput = codecs.open(targetpath, "r", "utf-8")
	fa_file = codecs.open(outpath + '.txt', "w", "utf-8")

	for sl, tl in zip(sourceinput, targetinput):
		sl = sl.strip().split("\t")[-1]
		tl = tl.strip().split("\t")[-1]
		fa_file.write(f"{sl} ||| {tl}\n")
	fa_file.close()
	return


def create_fwd_rev_files(outpath: str):
	if mode == "fastalign":
		os.system(f"{fastalign_path} -i {outpath}.txt -v -d -o > {outpath}.fwd")
		os.system(f"{fastalign_path} -i {outpath}.txt -v -d -o -r > {outpath}.rev")
	elif mode == "eflomal":
		os.system(f"cd {eflomal_path}; python align.py -i {outpath}.txt --model 3 -f {outpath}.fwd -r {outpath}.rev")
	return


def create_gdfa_file(outpath: str):
	# create gdfa file from .fwd and .rev
	os.system(f"{atools_path} -i {outpath}.fwd -j {outpath}.rev -c grow-diag-final-and > {outpath}_unnum.gdfa")

	# parse _unnum.gdfa to .gdfa with "\t" separator
	with codecs.open(f"{outpath}_unnum.gdfa", "r", "utf-8") as fi:
		with codecs.open(f"{outpath}.gdfa", "w", "utf-8") as fo:
			for i, line in enumerate(fi):
				fo.write(f"{i}\t{line.strip()}\n")

	# delete unnecessary files
	os.system(f"rm {outpath}_unnum.gdfa; rm {outpath}.fwd; rm {outpath}.rev; rm {outpath}.txt")
	return


def extract_alignments(i: int=-1, input_mode: bool=False):
	for num_symbols in merges:

		if input_mode:
			print(f"Alignments for input files")
			sourcepath = inputpath[source]
			targetpath = inputpath[target]
			outpath = join(bpedir, mode, f"input_{source}_{target}")
		else:
			print(f"Alignments for {num_symbols} symbols")
			if params[source]['bpe']:
				sourcepath = join(bpedir, 'segmentations', f"{source}_{num_symbols}{'_'+str(i) if dropout else ''}.bpe")
			else:
				sourcepath = inputpath[source]

			if params[target]['bpe']:
				targetpath = join(bpedir, 'segmentations',f"{target}_{num_symbols}{'_'+str(i) if dropout else ''}.bpe")
			else: 
				targetpath = inputpath[target]
			
			outpath = join(bpedir, mode, f"{num_symbols}{'_'+str(i) if i != -1 else ''}")

		create_parallel_text(sourcepath, targetpath, outpath)
		create_fwd_rev_files(outpath)
		create_gdfa_file(outpath)

		if input_mode:
			break

		# map alignment from subword to word
		bpes = load_and_map_segmentations(num_symbols, i)
		all_word_aligns = bpe_word_align(bpes, codecs.open(outpath+'.gdfa', encoding='utf-8'))
		os.system(f"rm {outpath}.gdfa")
		codecs.open(outpath+'.wgdfa', 'w', encoding='utf-8').write(all_word_aligns)

		print("\n\n")
	return


def merge_dropout_alignments():
    union_merge, inter_merge, thres_merge = {}, {}, {}
    for num_symbols in tqdm(merges, desc=f"merge_dropout: dropout={dropout}, thres"):
        union_merge[num_symbols], inter_merge[num_symbols], thres_merge[num_symbols] = [], [], []

        for i in range(dropout_samples):

            alpath = join(bpedir, mode, f"{num_symbols}_{i}.wgdfa")
            for j, line in enumerate(open(alpath, 'r').readlines()):
                al = frozenset(line.strip().split("\t")[1].split())

                # at the first iteration, just append the alignment
                if i == 0:
                    #union_merge[num_symbols].append(al)
                    #inter_merge[num_symbols].append(al)
                    thres_merge[num_symbols].append(Counter(al))
                    continue
                
                # do union, intersection or frequency addition
                #union_merge[num_symbols][j] |= al
                #inter_merge[num_symbols][j] &= al
                thres_merge[num_symbols][j] += Counter(al)

        # write to output
        os.chdir(join(bpedir, mode))
        #unionfile = codecs.open(f'{num_symbols}_union.wgdfa', 'w')
        #interfile = codecs.open(f'{num_symbols}_inter.wgdfa', 'w')
        thresfiles = {merge_t: codecs.open(f'{num_symbols}_thres_{merge_t}.wgdfa', 'w') for merge_t in merge_threshold}

        for i in range(len(union_merge[num_symbols])):
            #unionfile.write(f"{i}\t{' '.join(union_merge[num_symbols][i])}\n")
            #interfile.write(f"{i}\t{' '.join(inter_merge[num_symbols][i])}\n")

            # get alignments more common than the merge_threshold %
            for merge_t in merge_threshold:
                common_aligns = [k for k in thres_merge[num_symbols][i] 
                                if thres_merge[num_symbols][i][k] > merge_t * dropout_samples]
                thresfiles[merge_t].write(f"{i}\t{' '.join(common_aligns)}\n")
    return


if __name__ == "__main__":
	print(f"Extracting alignments: {json.dumps(params, indent=2)}")
	t0 = time.time()
	os.makedirs(join(bpedir, mode), exist_ok=True)
	if not os.path.isfile(join(bpedir, mode, f'input_{source}_{target}.gdfa')):
		extract_alignments(input_mode=True)

	if dropout > 0:
		for i in range(dropout_samples):
			print(f"Iteration {i+1}")
			extract_alignments(i)
		merge_dropout_alignments()
	else:
		extract_alignments()
	print(f"The process of extracting alignments took {str(timedelta(seconds=time.time()-t0))}")
