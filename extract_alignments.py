#!/usr/bin/env python3
import codecs
import argparse
import os.path
import os
import inspect

def add_numbers(input_file, output_file, start=0, max_num=-1):
	with codecs.open(input_file, "r", "utf-8") as fi, codecs.open(output_file, "w", "utf-8") as fo:
		count = start
		for l in fi:
			fo.write(str(count) + "\t" + l.strip() + "\n")
			count += 1
			if max_num > 0 and count >= max_num:
				break

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

	currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
	datapath = os.path.join(currentdir, 'data')

	# ubuntu
	fastalign_path = os.path.join(currentdir, "tools2/fast_align/build/fast_align")
	atools_path = os.path.join(currentdir, "tools2/fast_align/build/atools")

	# windows
	#currentdir = "C:/Users/anebe/Documents/Github/thesis/"
	#fastalign_path = os.path.join(currentdir, "tools/fast_align/build/fast_align")
	'''
	parser = argparse.ArgumentParser(description="Extract alignments with different models and store in files.", epilog="example: python extract_alignments.py -s file1 -t file2 -o output_file")
	parser.add_argument("-s", default="")
	parser.add_argument("-t", default="")
	parser.add_argument("-p", help="parallel text in fastalign format (if available)", default="")
	parser.add_argument("-o", help="the output_file path and name without extension")
	parser.add_argument("-m", choices=['fast', 'eflomal'], default="fast")
	args = parser.parse_args()
	'''

	all_symbols = [1000, 2000, 3000, 4000, 8000]
	for num_symbols in all_symbols:

		print(f"Alignments for {num_symbols} symbols")

		#s = os.path.join(currentdir, "data/input/eng_with_10k.txt")
		#t = os.path.join(currentdir, "data/input/deu_with_10k.txt")
		s = os.path.join(currentdir, "data/eng_"+str(num_symbols)+".bpe")
		t = os.path.join(currentdir, "data/deu_"+str(num_symbols)+".bpe")
		o = os.path.join(currentdir, "data/fastalign/"+str(num_symbols))
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

		# FastAlign
		if m == "fast":
			os.system("{} -i {} -v -d -o > {}.fwd".format(fastalign_path, p, o))
			os.system("{} -i {} -v -d -o -r > {}.rev".format(fastalign_path, p, o))
		# Eflomal
		elif m == "eflomal":
			os.system(eflomal_path + "align.py -i {0} --model 3 -f {1}.fwd -r {1}.rev".format(p, o))

		os.system("{0} -i {1}.fwd -j {1}.rev -c grow-diag-final-and > {1}_unnum.gdfa".format(atools_path, o))
		add_numbers(o + "_unnum.gdfa", o + ".gdfa")
		os.system("rm {}_unnum.gdfa".format(o))

		with open(o + ".fwd", "r") as f1, open(o + ".rev", "r") as f2, open(o + ".inter", "w") as fo:
			count = 0
			for l1, l2 in zip(f1, f2):
				l1 = set(l1.strip().split())
				l2 = set(l2.strip().split())
				fo.write(str(count) + "\t" + " ".join(sorted([x for x in l1 & l2])) + "\n")
				count += 1
