# thesis

Master thesis repo

## tasks

* [X] dropout + bpe_deu experiment
* [X] merge calc_align_score and avg_score
* [ ] source_bpe, target_bpe instead of german_bpe
* [ ] dropout only on source side?
* [ ] input + 1k symbols + 2k symbols, join them (dropout files). do intersection between alignments, union, threshold(if alignment appears in >k files, then it's a good alignment). if it doesn't work then we have to merge the file before fast align
* [ ] think about BPE on text without dropout. comple t ely. start from beginning?
* [ ] Read [unified LM tokenization paper](https://www.aclweb.org/anthology/P18-1007/)
  * bpe drooput similar results than ulm, but less computationally expensive
* [sentence piece](https://github.com/VKCOM/YouTokenToMe)

## bpe dropout

* with dropout is getting worse, check bpe dropout paper again how they do it
  * They produce multiple segmentations
  * During segmentation, at each merge step some merges are randomly dropped with probability p
  * using BPE-Dropout on the source side is more beneficial than using it on the target side
  * The improvement with respect to normal BPE are consistent no matter the vocabulary size. But the effect from using BPE-Dropout vanishes when a corpora size gets bigger.

## unigram LM paper

* [Comments on the paper](http://www.timoschick.com/paper%20picks/2020/04/14/bpe-is-suboptimal-for-lm-pretraining.html)

## scores

* In normal mode, BPE vs. gold standard
* In dropout mode, dropout BPE vs. BPE

## pipeline

1. Set parameters in `lib/__init__.py`
2. learn_bpe.py
3. apply_bpe.py
4. extract_alignments.py
5. calc_align_score.py

## directory structure

```
.
├── data
│   ├── input
│   │   ├── eng_with_10k.txt                          # input txt file with 10k english sentences
│   │   ├── deu_with_10k.txt
│   ├── normal_bpe
│   │   ├── fastalign                                 # files obtained from fastalign alignment algorithm
│   │   │   └── *.wgdfa, *_deu.wgdfa
│   │   ├── segmentations                             # files obtained by segmenting based on num_symbols
│   │   │   └── .bpe
│   │   └── scores.png, scores.csv
│   ├── dropout_bpe
│   │   ├── fastalign
│   │   │   └── *.wgdfa, *_deu.wgdfa
│   │   ├── segmentations
│   │   │   └── .bpe
│   │   ├── test_scores
│   │   │   └── .png, .csv
│   │   ├── merged                                     # TODO
│   │   │   └── ...
│   │   └── scores.png, scores.csv
│   ├── eng.model                                      # merge list for english
│   └── deu.model
├── README.md
├── .py
└── ...
```
