# tasks

## Minimal BPE algorithm

* [ ] BPE algorithm, merging
  * [X] get monolingual corpus
  * [~] Create minimal script of [learn_bpe.py](https://github.com/rsennrich/subword-nmt/blob/master/subword_nmt/learn_bpe.py)
  * [X] split all corpus to characters
  * [X] count bigrams in corpus (spaces excluded)
    * shouldn't merge space with anything, because then you merge 2 words together
    * some people replace them with an oov character so that it doesn't merge with anything, and in the end replace back to space
    * some people add end of word character so it doesn't merge with other words
  * [ ] find the most frequent one
  * [ ] start merging bigrams together until vocab size / N merges
  * [ ] for output, make merge list
* [X] Apply BPE to test

## resources

* apply bpe <https://github.com/rsennrich/subword-nmt/blob/master/subword_nmt/apply_bpe.py>
* best practices to apply bpe in nmt <https://github.com/rsennrich/subword-nmt/blob/master/README.md>
* sentence piece <https://github.com/VKCOM/YouTokenToMe>
