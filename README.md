# thesis

Master thesis repo

## tasks

* [ ] simplify learn_bpe
* [ ] add the baseline with another linestyle ("--"), so we can see the difference
* [ ] Use the normal text on one side and BPE on the other side. What's gonna happen? (Maybe BPE is only useful on the German side)
  * How to do subword_word.py like this?
* [ ] Try different vocab sizes, and maybe you see a difference. ex: 100, 200, 500, and 10k, 20k, 30k.

## questions

* Delete fastalign files? .for, .rev, .txt
* I don't have 10k+ vocab size

## pipeline

1. minimal_apply_bpe.py with num_symbols
2. extract_alignments.py
3. subword_word.py
4. calc_align_score.py

## resources

* sentence piece <https://github.com/VKCOM/YouTokenToMe>
