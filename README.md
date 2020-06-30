# thesis

Master thesis repo

* Alignment models: FastAlign, Eflomal
* Datasets: eng_deu, eng_fra
* Sampling methods: Dropout, (maybe something else?!)
* Tokenization: space mode, Chaos mode

## tasks

* [X] apply_bpe: do until 8k, and at 100, 500, 1k, 2k. write to output. but not do until 500, then until 1000.
* [ ] paper stuff, do after thesis
  * no space is good language with no space tokenization
  * eflomal instead of fastalign? https://github.com/robertostling/eflomal result will probably not be as good
  * english - french, english - romanian (Masoud has datasets)
* [ ] BPE algo is very slow, everyone uses [fastBPE](https://github.com/glample/fastBPE)
* [ ] check SentencePiece
* [ ] pipeline: if we discard `we _`, then all possibilities of `we_ X` won't be considered. Huge loss of merges
* [ ] extract_alignments: maybe do fast align in one big file? both ways seem to work
* [ ] learn_bpe: substitute number for digit when merging? it's a good thing that these are rare. This way, we only merge a digit with a character only if it's frequent.
* [ ] dropout only on one side? source_bpe -> source_dropout? Since they experiment on MT, the situation is totally different. It might be interesting to see if there's a difference or not. Alignments are bidirectional. If you want to try this, you should try it for both sides and merge them:
  * Normal_source Sample_target_1
  * Normal_source Sample_target_2
  * Normal_source Sample_target_3
  * Sample_source_1 Normal_target
  * Sample_source_2 Normal_target
  * Sample_source_3 Normal_target

### BPE improvement

* [ ] BPE improvement without dropout. comple t ely
  * divide and conquer, first make big chunks then merge them together instead of adding characters to the biggest chunk one by one
  * I assigned a score to BPEs based on their **depth of merge tree**. the depth score
  * When applying the BPE model to the text, I would give priority to the high score BPEs.
  * book. bo ok -> book. min merge tree depth is 2. could also be 3, bo, boo, book. to get more meaningful chunks
  * t h, both 0, then th:1. th:1, e:0, the:2
  * un:1 accept:3 able:3. acceptable has higher score than unaccept. if 2 chunks have same score, join the larger ones.

## pipeline

1. Set parameters in `settings.py`
2. learn_bpe.py
3. apply_bpe.py
4. extract_alignments.py (can be done in parallel to apply_bpe, after an offset of ~2 elements)
5. calc_align_score.py / merge_dropout.py

## directory structure

```
.
├── data
│   ├── input
│   │   ├── eng_with_10k.txt                          # input txt file with 10k english sentences
│   │   └── deu_with_10k.txt
│   ├── normal_bpe
│   │   ├── fastalign                                 # files obtained from fastalign alignment algorithm
│   │   │   └── *.wgdfa, *_deu.wgdfa
│   │   └── segmentations                             # files obtained by segmenting based on num_symbols
│   │       └── .bpe
│   ├── dropout_bpe
│   │   ├── fastalign
│   │   │   └── *.wgdfa, *_deu.wgdfa, *_union.wgdfa, *_inter.wgdfa, *_thres.wgdfa
│   │   └── segmentations
│   │       └── .bpe
│   ├── eng.model                                      # merge list for english
│   └── deu.model
├── doc
├── reports
│   ├── scores_dropout_bpe
│   │   └── *.csv, *.png
│   └── scores_normal_bpe
│       └── *.csv, *.png
├── README.md
├── .py
└── ...
```

## resources

* [Huggingface tokenizers](https://github.com/huggingface/tokenizers)
* [You token to me](https://github.com/VKCOM/YouTokenToMe)
* [Comments on the unigram LM paper](http://www.timoschick.com/paper%20picks/2020/04/14/bpe-is-suboptimal-for-lm-pretraining.html)
