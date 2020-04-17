# thesis

Master thesis repo

## tasks

* [X] Check that . can be present in merge list
* [X] b ut w e -> [0, 0, 1, 1] to which word does each bpe belong to. do with both langs
* [ ] get bpe alignments
* [ ] bpe alignment -> word alignment
  * 1 in the bpe list belongs to word nº0
* [ ] do calc_score with gold from data
* [ ] check calc_score for normal input, what's the good bpe size, 2k, 5k?
* [ ] figure, bpe size vs. alignment quality / score

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
