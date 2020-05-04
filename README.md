# thesis

Master thesis repo

## tasks

* [X] do the same dropout test 3,5,10 times, check scores, average scores. because dropout is different each time. maybe one sample is really good
* [ ] average dropouts
* [ ] make a training data with 100k sentences by putting 10 samples together and then look at the quality of their aggregation. put samples one after another, get alignments, that way we get a bigger trainset.
* [ ] http://www.timoschick.com/paper%20picks/word%20level%20semantics/2020/04/14/bpe-is-suboptimal-for-lm-pretraining.html
* [ ] https://arxiv.org/abs/1910.07181
* [ ] https://arxiv.org/abs/2001.07676

## questions

* with dropout is getting worse, check bpe dropout paper again how they do it
  * They produce multiple segmentations
  * During segmentation, at each merge step some merges are randomly dropped with probability p
  * using BPE-Dropout on the source side is more beneficial than using it on the target side
  * The improvement with respect to normal BPE are consistent no matter the vocabulary size. But we see that the effect from using BPE-Dropout vanishes when a corpora size gets bigger.

## pipeline

1. minimal_apply_bpe.py with num_symbols
2. extract_alignments.py
3. subword_word.py
4. calc_align_score.py

## resources

* sentence piece <https://github.com/VKCOM/YouTokenToMe>
