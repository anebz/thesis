# thesis

Master thesis repo

* Alignment models: FastAlign, Eflomal
* Datasets: eng_deu, eng_fra
* Sampling methods: Dropout, (maybe something else?!)
* Tokenization: space mode, Chaos/no space mode

## tasks

* [ ] extract_alignments: maybe do fast align in one big file? both ways seem to work

### BPE improvement, after thesis

* [ ] BPE improvement without dropout. comple t ely
  * divide and conquer, first make big chunks then merge them together instead of adding characters to the biggest chunk one by one
  * I assigned a score to BPEs based on their **depth of merge tree**. the depth score
  * When applying the BPE model to the text, I would give priority to the high score BPEs.
  * book. bo ok -> book. min merge tree depth is 2. could also be 3, bo, boo, book. to get more meaningful chunks
  * t h, both 0, then th:1. th:1, e:0, the:2
  * un:1 accept:3 able:3. acceptable has higher score than unaccept. if 2 chunks have same score, join the larger ones.

## resources

* [You token to me](https://github.com/VKCOM/YouTokenToMe)
* [Comments on the unigram LM paper](http://www.timoschick.com/paper%20picks/2020/04/14/bpe-is-suboptimal-for-lm-pretraining.html)
