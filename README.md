# thesis

Master thesis repo

## tasks

* [ ] dropout only on one side? source_bpe -> source_dropout?
* [X] dropout vs. merge_threshold test
  * Tested with all_symbols=[2000, 4000] and dropout_iterations
  * bpe_dropout paper has highest score at dropout=0.1, dropout_iterations=10, merge_threshold=0.6 with f1=0.669
  * my tests have highest score at dropout=0.3, dropout_iterations=30, merge_threshold=0.5 with f1=0.685
  * same result at dropout=0.2, dropout_iterations=30, merge_threshold=0.5 with f1=0.684
  * for dropout=0.1, no difference between dropout_iterations=10 or 30
* [ ] think about BPE on text without dropout. comple t ely
  * Prioritize affixes and suffixes

## done this week

* union, intersection, threshold for bpe_dropout. significant improvements (`data/dropout_bpe/scores`)
* Read [unified LM tokenization paper](https://www.aclweb.org/anthology/P18-1007/)

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
5. calc_align_score.py / merge_dropout.py

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
│   │   │   └── *.wgdfa, *_deu.wgdfa, *_unionwgdfa, *_inter.wgdfa, *_thres.wgdfa
│   │   ├── segmentations
│   │   │   └── .bpe
│   │   ├── test_scores
│   │   │   └── .png, .csv
│   │   └── scores.png, scores.csv
│   ├── eng.model                                      # merge list for english
│   └── deu.model
├── README.md
├── .py
└── ...
```

## resources

* [Huggingface tokenizers](https://github.com/huggingface/tokenizers)
* [You token to me](https://github.com/VKCOM/YouTokenToMe)