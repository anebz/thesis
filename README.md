# thesis

Master thesis repo

## tasks

* [ ] simplify learn_bpe
* [X] Use the normal text on one side and BPE on the other side. Maybe BPE is only useful on the German side
* [ ] with dropout is getting worse, check bpe dropout paper again how they do it
* [ ] do the same dropout test like 3,5,10 times, check scores, average scores. because dropout is different each time. maybe one sample is really good
* [ ] make a training data with 100k sentences by putting 10 samples together and then look at the quality of their aggregation. put samples one after another, get alignments, that way we get a bigger trainset.

## pipeline

1. minimal_apply_bpe.py with num_symbols
2. extract_alignments.py
3. subword_word.py
4. calc_align_score.py

## resources

* sentence piece <https://github.com/VKCOM/YouTokenToMe>
