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

TODO run again

| Lang pairs | num_merges | Precision | Recall | F1 score | AER   |
| ---------- |:----------:|:---------:|:------:|:--------:|:-----:|
| eng-deu    |            | 0.099     | 0.082  | 0.09     | 0.91  |
| eng-hin    |            | 0.075     | 0.064  | 0.069    | 0.931 |

### 2. word - BPE-no-space

align_thres=0.7, target_bpe=True. scores in `eports/scores_normal_bpe/eng_X_ns_fastalign.csv`

Scores for BPE-no-space - BPE-no-space

| Lang pairs | num_merges | Precision | Recall | F1 score | AER   |
| ---------- |:----------:|:---------:|:------:|:--------:|:-----:|
| eng-deu    | 200        | 0.406     | 0.578  | 0.477    | 0.524 |
| eng-deu    | 500        | 0.384     | 0.555  | 0.454    | 0.548 |

-----

| Lang pairs | num_merges | Precision | Recall | F1 score | AER   |
| ---------- |:----------:|:---------:|:------:|:--------:|:-----:|
| eng-hin    | 200        | 0.244     | 0.35   | 0.288    | 0.712 |
| eng-hin    | 500        | 0.215     | 0.322  | 0.258    | 0.742 |

Scores for word - BPE-no-space

| Lang pairs | num_merges | Precision | Recall | F1 score  | AER   |
| ---------- |:----------:|:---------:|:------:|:------ --:|:-----:|
| eng-deu    | 200        | 0.456     | 0.526  | **0.489** | 0.512 |
| eng-deu    | 500        | 0.437     | 0.535  | 0.481     | 0.52  |
| eng-hin    | 200        | 0.277     | 0.317  | **0.296** | 0.704 |
| eng-hin    | 500        | 0.245     | 0.322  | 0.278     | 0.722 |

### 3. word - BPE-no-space-dropout

dropout=0.2, align_thres=0.5, target_bpe=True. Scores in `reports/scores_dropout_bpe/no space/0.2/eng_X_ns_0.5_thres_fastalign_X.csv`

| Lang pairs | num_merges | Precision | Recall | F1 score  | AER   |
| ---------- |:----------:|:---------:|:------:|:---------:|:-----:|
| eng-deu    | 200        | 0.582     | 0.487  | 0.53      | 0.469 |
| eng-deu    | 500        | 0.61      | 0.497  | **0.548** | 0.452 |

-----

| Lang pairs | num_merges | Precision | Recall | F1 score  | AER   |
| ---------- |:----------:|:---------:|:------:|:---------:|:-----:|
| eng-hin    | 200        | 0.404     | 0.281  | 0.331     | 0.669 |
| eng-hin    | 500        | 0.394     | 0.292  | **0.335** | 0.665 |

better results than #exp2

### 4. BPE-space - BPE-no-space

| Lang pairs | num_merges | Precision | Recall | F1 score  | AER   |
| ---------- |:----------:|:---------:|:------:|:---------:|:-----:|
| eng-deu    | 200        | 0.422     | 0.583  | 0.49      | 0.511 |
| eng-deu    | 500        | 0.447     | 0.6    | **0.512** | 0.489 |
| eng-deu    | 1000       | 0.392     | 0.54   | 0.454     | 0.547 |
| eng-deu    | 2000       | 0.325     | 0.487  | 0.39      | 0.612 |

-----

| Lang pairs | num_merges | Precision | Recall | F1 score  | AER   |
| ---------- |:----------:|:---------:|:------:|:---------:|:-----:|
| eng-hin    | 200        | 0.266     | 0.367  | **0.308** | 0.692 |
| eng-hin    | 500        | 0.244     | 0.343  | 0.285     | 0.715 |
| eng-hin    | 1000       | 0.193     | 0.296  | 0.234     | 0.766 |
| eng-hin    | 2000       | 0.152     | 0.268  | 0.194     | 0.806 |

Better F1 than #exp2

### 5. BPE-space - BPE-no-space-dropout

| Lang pairs | num_merges | Precision | Recall | F1 score  | AER   |
| ---------- |:----------:|:---------:|:------:|:---------:|:-----:|
| eng-deu    | 200        | 0.523     | 0.538  | 0.53      | 0.47  |
| eng-deu    | 500        | 0.607     | 0.557  | **0.581** | 0.419 |
| eng-deu    | 1000       | 0.63      | 0.532  | 0.577     | 0.423 |
| eng-deu    | 2000       | 0.59      | 0.478  | 0.528     | 0.472 |

-----

| Lang pairs | num_merges | Precision | Recall | F1 score  | AER   |
| ---------- |:----------:|:---------:|:------:|:---------:|:-----:|
| eng-hin    | 200        | 0.358     | 0.341  | 0.349     | 0.651 |
| eng-hin    | 500        | 0.407     | 0.331  | **0.365** | 0.635 |
| eng-hin    | 1000       | 0.357     | 0.306  | 0.33      | 0.67  |
| eng-hin    | 2000       | 0.294     | 0.255  | 0.273     | 0.727 |

### 6. BPE-space-dropout - BPE-no-space-dropout

dropout=0.2, align_thres=0.5

| Lang pairs | num_merges | Precision | Recall | F1 score  | AER   |
| ---------- |:----------:|:---------:|:------:|:---------:|:-----:|
| eng-deu    | 200        | 0.567     | 0.516  | 0.54      | 0.46  |
| eng-deu    | 500        | 0.621     | 0.556  | **0.587** | 0.413 |
| eng-deu    | 1000       | 0.641     | 0.537  | 0.584     | 0.415 |
| eng-deu    | 2000       | 0.603     | 0.49   | 0.541     | 0.459 |

-----

| Lang pairs | num_merges | Precision | Recall | F1 score  | AER   |
| ---------- |:----------:|:---------:|:------:|:---------:|:-----:|
| eng-hin    | 200        | 0.351     | 0.319  | 0.334     | 0.666 |
| eng-hin    | 500        | 0.404     | 0.328  | **0.362** | 0.638 |
| eng-hin    | 1000       | 0.338     | 0.296  | 0.316     | 0.685 |
| eng-hin    | 2000       | 0.313     | 0.266  | 0.288     | 0.712 |
