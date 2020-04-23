# thesis

Master thesis repo

## tasks

* [ ] simplify learn_bpe
* [ ] add the baseline with another linestyle ("--"), so we can see the difference
  * [ ] change matplotlib linestyle to see the baseline results
* [ ] Use the normal text on one side and BPE on the other side. What's gonna happen? (Maybe BPE is only useful on the German side)
* [ ] Try different num_symbol sizes, and maybe you see a difference. ex: 100, 200, 500, and 10k, 20k, 30k.
* [ ] plot alias, axis
* [ ] with dropout is getting worse, check bpe dropout paper again how they do it
* [ ] do the same dropout test like 3,5,10 times, check scores, average scores. because dropout is different each time. maybe one sample is really good
* [ ] what if we make a training data with 100k sentences by putting 10 samples together and then look at the quality of their aggregation. put samples one after another, get alignments, that way we get a bigger trainset.

## questions

* Delete fastalign files? .for, .rev, .txt
  * gdfa has high recall, less accurate
  * inter is high precision
  * for and rev in gitignore

## pipeline

1. minimal_apply_bpe.py with num_symbols
2. extract_alignments.py
3. subword_word.py
4. calc_align_score.py

## resources

* sentence piece <https://github.com/VKCOM/YouTokenToMe>
