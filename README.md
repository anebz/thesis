# thesis

Master thesis repo

## tasks

* [ ] summary of my learn_bpe vs. paper learn_bpe, differences, is this paper material? track algorithm performance in my computer, write in percentage. this algo is 1.4% faster than X.
* [ ] dropout only on one side? source_bpe -> source_dropout?
* [ ] save most_frequent in list and write in the end. Also write correct \# of merges created, if there's a break

### BPE improvement

* [ ] BPE improvement without dropout. comple t ely
  * divide and conquer, first make big chunks then merge them together instead of adding characters to the biggest chunk one by one
  * I assigned a score to BPEs based on their **depth of merge tree**. the depth score
  * When applying the BPE model to the text, I would give priority to the high score BPEs.
  * book. bo ok -> book. min merge tree depth is 2. could also be 3, bo, boo, book. to get more meaningful chunks
  * t h, both 0, then th:1. th:1, e:0, the:2
  * un:1 accept:3 able:3. acceptable has higher score than unaccept. if 2 chunks have same score, join the larger ones.

### no space

* [ ] no space mode
  * [ ] **learn_bpe**
    * [X] use optimized method for space mode
      * [X] Some merges are duplicated in `space` mode
      * [X] Keep freq of pairs per sentence in idx?
    * [~] Adapt learn_bpe for both modes
  * [ ] apply_bpe
  * [ ] alignments
  * `['_The', 'e_'. 'ice_cre', 'am'] word_belonging = [[0], [0], [1,2], [2]]`. now for each bpe we have a list of words, it was the other way before. each word could have 1+ bpes, now each bpe can have 1+ words. we have no spaces so even f1=0.5 would be great. we'd be aligning words even if we don't know they exist. then we could go for more precision-based model or recall-based model. alignment w/o tokenization

## pipeline

1. Set parameters in `settings.py`
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
* [Comments on the unigram LM paper](http://www.timoschick.com/paper%20picks/2020/04/14/bpe-is-suboptimal-for-lm-pretraining.html)
