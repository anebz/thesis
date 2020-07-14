# Thesis document outline

1. [ ] Introduction
2. [ ] Motivation
3. [X] Tokenization
4. [~] Translation
5. [X] Methodology
6. [X] Development
7. Results, experiments, analysis, challenges, how to choose a good baseline, figures
   1. BPE results
   2. BPE dropout results
   3. learn_bpe improvement performance
8. ...
9. Future work
10. Conclusion

## learn_bpe algorithm

* summary of my learn_bpe vs. paper learn_bpe, differences, is this paper material? track algorithm performance in my computer, write in percentage. this algo is 1.4% faster than X.

## bpe dropout

* with dropout is getting worse, check bpe dropout paper again how they do it
  * They produce multiple segmentations
  * During segmentation, at each merge step some merges are randomly dropped with probability p
  * using BPE-Dropout on the source side is more beneficial than using it on the target side
  * The improvement with respect to normal BPE are consistent no matter the vocabulary size. But the effect from using BPE-Dropout vanishes when a corpora size gets bigger.

## scores

* In normal mode, BPE vs. gold standard
* In dropout mode, dropout BPE vs. BPE

* bpe_dropout paper has highest score at dropout=0.1, dropout_iterations=10, merge_threshold=0.7 with f1=0.666
* my tests have highest score at dropout=0.3, dropout_iterations=30, merge_threshold=0.5 with f1=0.685
* same result at dropout=0.2, dropout_iterations=30, merge_threshold=0.5 with f1=0.684
* for dropout=0.1, no difference between dropout_iterations=10 or 30

## no_space learn_bpe results

* space: 0.49/0:54/0:56/1:52 eng, 1:19/1:16/1:28/2:36 deu
* no_space 10k symbols: 4/6:13 eng, 4:25/4:50 deu
* no_space 20k symbols: 9:33 eng, 10:10 deu

## no space results

* results:
  * at smallest threshold (0.3), recall=0.533 for all symbols, precision decreases for more symbols
  * the bigger the threshold, the worse the recall. at thres=0.9, precision isn't bad.
  * union score has very high recall, very low precision. makes sense, there's many-to-many alignment among words
  * intersection score has very high precision, very low recall
* we have no spaces so even f1=0.5 would be great. we'd be aligning words even if we don't know they exist. then we could go for more precision-based model or recall-based model. alignment w/o tokenization

* dropout=0,   best result at merge_threshold=0.5, num_symbols=200, f1=0.477
* dropout=0.1, best result at merge_threshold=0.7, num_symbols=200, f1=0.523
* dropout=0.2, best result at merge_threshold=0.5, num_symbols=500, **f1=0.559**
* dropout=0.3, best result at merge_threshold=0.5, num_symbols=500, f1=0.556
* dropout=0.4, best result at merge_threshold=0.3, num_symbols=500, f1=0.532
* dropout=0.5, best result at merge_threshold=0.3, **num_symbols=4000**, f1=0.529

## directory structure

```
.
├── data
│   ├── input
│   │   ├── eng_with_10k.txt   # input txt file with 10k english sentences
│   │   ├── deu_with_10k.txt
│   │   └── eng_deu.gold       # gold standard alignments for English-German
│   ├── normal_bpe
│   │   ├── segmentations      # files obtained by segmenting based on num_symbols and lang
│   │   │   └── *.bpe
│   │   ├── fastalign          # files obtained from fastalign alignment algorithm
│   │   │   └── .wgdfa
│   │   └── eflomal            # files obtained from eflomal alignment algorithm
│   │       └── .wgdfa
│   ├── dropout_bpe
│   │   ├── segmentations                             
│   │   │   └── *.bpe
│   │   ├── fastalign                                 
│   │   │   └── *.wgdfa
│   │   └── eflomal                                   
│   │       └── *.wgdfa
│   ├── eng.model              # merge list for english, space mode
│   ├── deu.model
│   ├── eng_ns.model           # merge list for english, no space mode
│   └── deu_ns.model
├── doc                        # LaTeX files for the writing of the thesis
│   ├── figures
│   ├── sections
│   └── *.tex files
├── reports
│   ├── scores_normal_bpe      # scores for BPE depending on normal/dropout, space/no space, etc.
│   │   └── *.csv, *.png
│   └── scores_dropout_bpe
│       └── *.csv, *.png
├── src                        # python files
│   ├── learn_bpe.py
│   ├── apply_bpe.py
│   ├── extract_alignments.py
│   ├── calc_align_score.py
│   └── merge_dropout.py
├── tools                        # fastalign, eflomal installation directories
│   ├── fastalign
│   └── eflomal
├── .gitignore
├── README.md
├── requirements.txt
└── settings.py
```

## pipeline

1. Set parameters in `settings.py`
2. learn_bpe.py
3. apply_bpe.py
4. extract_alignments.py (can be done in parallel to apply_bpe, after an offset of ~2 elements)
5. calc_align_score.py / merge_dropout.py
=======
## open questions

* learn_bpe: substitute number for digit when merging? it's a good thing that these are rare. This way, we only merge a digit with a character only if it's frequent.
* dropout only on one side? source_bpe -> source_dropout? Since they experiment on MT, the situation is totally different. It might be interesting to see if there's a difference or not. Alignments are bidirectional. If you want to try this, you should try it for both sides and merge them:
  * Normal_source Sample_target_1
  * Normal_source Sample_target_2
  * Normal_source Sample_target_3
  * Sample_source_1 Normal_target
  * Sample_source_2 Normal_target
  * Sample_source_3 Normal_target
