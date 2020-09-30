#!/bin/sh
python src/apply_bpe.py
python src/extract_alignments.py
python src/calc_align_score.py
