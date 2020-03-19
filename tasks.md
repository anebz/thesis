# tasks

## 19 March

* [ ] BPE algorithm, merging
    - [ ] get monolingual corpus
    - [ ] split all chars
    - [ ] start merging together until vocab size
        + shouldn't merge space with anything, because then you merge 2 words together
        + some people replace with an oov character so that it doesn't merge with anything, and in the end replace back to space
        + some people add end of word character so it doesn't merge with other words
    - [ ] for output, make merge list
* [ ] Apply BPE to test

#### resources

* apply bpe https://github.com/rsennrich/subword-nmt/blob/master/subword_nmt/apply_bpe.py
* best practices to apply bpe in nmt https://github.com/rsennrich/subword-nmt/blob/master/README.md
* https://github.com/VKCOM/YouTokenToMe sentence piece
