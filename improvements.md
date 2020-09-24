# Improvements

* [ ] BPE improvement without dropout. comple t ely
  * divide and conquer, first make big chunks then merge them together instead of adding characters to the biggest chunk one by one
  * I assigned a score to BPEs based on their depth of merge tree. the depth score
  * When applying the BPE model to the text, I would give priority to the high score BPEs.
  * bo ok -> book. min merge tree depth is 2. could also be 3, bo, boo, book. to get more meaningful chunks
  * t h, both 0, then th:1. th:1, e:0, the:2
  * un:1 accept:3 able:3. acceptable has higher score than unaccept. if 2 chunks have same score, join the larger ones

From [Byte Pair Encoding is Suboptimal for Language Model Pretraining, Bostrom et al., 2020](https://github.com/anebz/papers/blob/master/2020/2004.03720.md)

> Recognizable affixes appear much more frequently in ULM. As the BPE tokenization is constructed greedily according to frequency, common affixes and punctuation) are frequently absorbed into other tokens. BPE vocabulary still includes these affixes, but when they are encountered during tokenization, they are almost always merged into larger units.

Example of 3 characters

> In the case where three tokens almost always occur as a group, in order to merge them into a single token, BPE must first merge one pair before incorporating the third token; this leaves an intermediate token in the vocabulary that will only occur rarely on its own. The unigram LM method avoids this pathology by considering all potential subwords in a top-down fashion during vocabulary selection.

**The unigram LM tokenization tends to have longer subword units than BPE.**

## First implementation

* Scoring system, the higher the pair length, higher score
* Fast merging of long words: important, particular, proposal, therefore

## Extended experiments

format: num_merges,prec,rec,f1,AER

### 1. word - char

* eng-deu: ,0.099,0.082,0.09,0.91
* eng-hin: ,0.075,0.064,0.069,0.931

### 2. word - BPE-no-space

previously refers to BPE-no-space - BPE-no-space

* eng-deu previously
  * 200,0.406,0.578,0.477,0.524
  * 500,0.384,0.555,0.454,0.548
* eng-deu now
  * 200,0.456,0.526,**0.489**,0.512
  * 500,0.437,0.535,**0.481**,0.52
* eng-hin previously
  * 200,0.244,0.35,0.288,0.712
  * 500,0.215,0.322,0.258,0.742
* eng-hin now
  * 200,0.277,0.317,**0.296**,0.704
  * 500,0.245,0.322,**0.278**,0.722
