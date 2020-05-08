# thesis

Master thesis repo

## tasks

* [ ] compare bpe & bpe_dropout
* [ ] test whole pipeline with deu as source, eng as target
* [ ] do normal_eng & bpe_deu again, both sides, fewer symbols
* [ ] dropout + bpe_deu experiment
* [ ] https://arxiv.org/abs/2004.03720
* [ ] http://www.timoschick.com/paper%20picks/2020/04/14/bpe-is-suboptimal-for-lm-pretraining.html
* [ ] https://arxiv.org/abs/1910.07181
* [ ] https://arxiv.org/abs/2001.07676

## bpe dropout

* with dropout is getting worse, check bpe dropout paper again how they do it
  * They produce multiple segmentations
  * During segmentation, at each merge step some merges are randomly dropped with probability p
  * using BPE-Dropout on the source side is more beneficial than using it on the target side
  * The improvement with respect to normal BPE are consistent no matter the vocabulary size. But the effect from using BPE-Dropout vanishes when a corpora size gets bigger.

## pipeline

1. minimal_apply_bpe.py with num_symbols
2. extract_alignments.py
3. subword_word.py
4. calc_align_score.py

## directory structure

.
├── data
│   ├── input
│   │   ├── eng_with_10k.txt                          # input txt file with 10k english sentences
│   │   ├── deu_with_10k.txt
│   ├── normal_bpe
│   │   ├── fastalign                                 # files obtained from fastalign alignment algorithm
│   │   │   └── .fwd, .gdfa, .inter, .rev, .txt
│   │   ├── segmentations                             # files obtained by segmenting based on num_symbols
│   │   │   └── .bpe
│   │   └── scores.png, scores.csv
│   ├── dropout_bpe
│   │   ├── fastalign
│   │   │   └── .fwd, .gdfa, .inter, .rev, .txt
│   │   ├── segmentations
│   │   │   └── .bpe
│   │   ├── scripts                                    # TODO
│   │   │   └── ...
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

## resources

* sentence piece <https://github.com/VKCOM/YouTokenToMe>
