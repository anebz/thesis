# thesis

Repository for my Master thesis on **The effects of word segmentation quality on word alignments**. The thesis PDF can be found [here](https://github.com/anebz/thesis/blob/master/doc/main.pdf). This repository handles the following functions:

* Datasets: English-German, English-Romanian, English-Hindi. To any other datasets, add a folder with the names of the language pairs in `data/input` and under it the txt files with the following format: 'eng_with_X.txt', for X number of sentences and for both languages, and the gold standard. See examples in `data/input` 
* Alignment models: Fastalign, Eflomal. For installation, see section 5.2.3. of the [thesis](https://github.com/anebz/thesis/blob/master/doc/main.pdf)
* Sampling methods: Dropout
* Tokenization: space mode, no space mode

These parameters and others can be set in `settings.py`.
