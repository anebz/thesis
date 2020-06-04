# Thesis document outline

1. Introduction
2. State of the art
   1. Tokenization
      1. Tokenization methods
      2. BPE
      3. BPE dropout
   2. Translation
      1. NMT? open vocabulary problems?
3. Development
   1. Coding practices
   2. Implementation of BPE
      1. Learn BPEs
      2. Apply BPEs
      3. Align BPEs
      4. Calculate BPE scores
   3. Implementation of BPE dropout
   4. Implementation of BPE dropout on source or target side
   5. Improvement over BPE dropout
   6. ...
4. ...
5. Future work
6. Conclusion

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

* space: 0.49/0:56/1:52 eng, 1:19/1:28/2:36 deu
* no_space: 4/6:13 eng, 4:25/4:50 deu