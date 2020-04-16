# tasks

```bash
python script.py |& tee file.txt
```

## Small things

* [X] **leave the _ at beginning of word**
* [X] don't delete periods
* [X] add metadata to model like language, number of symbols
* [X] .model for model, .bpe for outputs

## Next things

* [ ] calc_score with gold from data
* [ ] b ut w e -> [0, 0, 1, 1] to which word does each bpe belong to. do with both langs
* [ ] we get bpe alignments like 1-2, 3-4, 4-5. we want to transform to word alignments, so 1 in the bpe list belongs to word nº0. bpe alignment -> word alignment
* [ ] do calc_score
* [ ] check calc_score for normal input, what's the good bpe size, 2k, 5k?
* [ ] figure, bpe size vs. alignment quality / score
* [ ] think how to apply bpe dropout in our method, where. in apply_bpe

```python
BPE to word mapping example:
_B ut _this _is _not _wh at _ha pp en s
e_bpe_map: [0, 0, 1, 2, 3, 4, 4, 5, 5, 5, 5]

bpe_aligns: 1-2 4-5 4-6
word_aligns = [(e_bpe_map[p[0]], d_bpe_map[p[1]]) for p in bpe_aligns]

word_aligns: 0-1

d_bpe_map: [0, 0, 1, 2, 3, 4, 4, 5, 5, 6, 7, 7, 7, 8]
```

## resources

* sentence piece <https://github.com/VKCOM/YouTokenToMe>
