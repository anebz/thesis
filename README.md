# thesis

Master thesis repo

## tasks

* [ ] **interpret results**
* [ ] learn_bpe: substitute number for digit when merging?
* [X] replace sep token by 'sep', put in settings?
* [ ] merge_dropout: iterate through thres, don't calculate union and int every time
* [ ] calc_align_score: add legend to tqdm? script name, lang, num_symbols
* [ ] calc_align_score: only plot symbols present in the alignment files, not the baselines. otherwise we get [500, 8000] for all
* [ ] dropout only on one side? source_bpe -> source_dropout?

### BPE improvement

* [ ] BPE improvement without dropout. comple t ely
  * divide and conquer, first make big chunks then merge them together instead of adding characters to the biggest chunk one by one
  * I assigned a score to BPEs based on their **depth of merge tree**. the depth score
  * When applying the BPE model to the text, I would give priority to the high score BPEs.
  * book. bo ok -> book. min merge tree depth is 2. could also be 3, bo, boo, book. to get more meaningful chunks
  * t h, both 0, then th:1. th:1, e:0, the:2
  * un:1 accept:3 able:3. acceptable has higher score than unaccept. if 2 chunks have same score, join the larger ones.

### no space

* results:
  * at smallest threshold (0.3), recall=0.533 for all symbols, precision decreases for more symbols
  * the bigger the threshold, the worse the recall. at thres=0.9, precision isn't bad.
  * union score has very high recall, very low precision
  * intersection score has very high precision, very low recall
* we have no spaces so even f1=0.5 would be great. we'd be aligning words even if we don't know they exist. then we could go for more precision-based model or recall-based model. alignment w/o tokenization

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
