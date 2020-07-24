# Thesis document outline

1. [ ] Introduction
2. [ ] Motivation
3. [X] Tokenization
4. [~] Translation
5. [X] Methodology
6. [X] Development
7. [ ] Results
8. ...
9. Future work
10. Conclusion

## directory structure

```
.
├── data
│   ├── input
│   │   ├── eng-deu
│   │   │   ├── eng_with_10k.txt   # input txt file with 10k english sentences
│   │   │   ├── deu_with_10k.txt
│   │   │   ├── eng_deu.gold       # gold standard alignments for English-German
│   │   │   ├── eng.model          # merge list for english, space mode
│   │   │   ├── deu.model
│   │   │   ├── eng_ns.model       # merge list for english, no space mode
│   │   │   └── deu_ns.model
│   │   ├── eng-ron
│   │   └── eng-hin
│   ├── normal_bpe
│   │   ├── segmentations      # files obtained by segmenting based on num_symbols and lang
│   │   │   └── *.bpe
│   │   ├── fastalign          # files obtained from fastalign alignment algorithm
│   │   │   └── .wgdfa
│   │   └── eflomal            # files obtained from eflomal alignment algorithm
│   │       └── .wgdfa
│   └── dropout_bpe
│       ├── segmentations
│       │   └── *.bpe
│       ├── fastalign
│       │   └── *.wgdfa
│       └── eflomal
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
