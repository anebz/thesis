# thesis

Repository for my Master thesis on **The effects of word segmentation quality on word alignments**. The thesis PDF can be found [here](https://github.com/anebz/thesis/blob/master/doc/main.pdf). This repository handles the following functions:

* Datasets: English-German, English-Romanian, English-Hindi. To any other datasets, add a folder with the names of the language pairs in `data/input` and under it the txt files with the following format: 'eng_with_X.txt', for X number of sentences and for both languages, and the gold standard. See examples in `data/input` 
* Alignment models: Fastalign, Eflomal
* Sampling methods: Dropout
* Tokenization: space mode, no space mode

These parameters and others can be set in `settings.py`.

## Installation and run

Fastalign installation

```bash
sudo apt-get install libgoogle-perftools-dev libsparsehash-dev
cd /path/to/project
mkdir tools
cd tools
git clone https://github.com/clab/fast_align.git
cd fast_align
mkdir build
cd build
cmake ..
make
```

Eflomal installation

```bash
cd /path/to/project/tools
git clone https://github.com/robertostling/eflomal.git
cd eflomal
make
sudo make install
python3 setup.py install
```

Install dependencies

```bash
pip -r install requirements.txt
```

Modify `settings.py` for your desired parameters. To run all pipeline:

```bash
./run.sh
```

## Project structure

```
.
├── data
│   ├── input
│   │   ├── eng-deu
│   │   │   ├── eng_with_10k.txt   # input txt file with 10k english sentences
│   │   │   ├── deu_with_10k.txt
│   │   │   ├── eng_deu.gold       # gold standard alignments
│   │   │   ├── eng.model          # merge list for english, space mode
│   │   │   ├── deu.model
│   │   │   ├── eng_ns.model       # merge list for english, no space mode
│   │   │   └── deu_ns.model
│   │   ├── eng-ron
│   │   └── eng-hin
│   ├── normal_bpe
│   │   ├── segmentations      # files obtained by applying BPE to corpus
│   │   │   └── *.bpe
│   │   ├── fastalign          # files obtained from fastalign 
│   │   │   └── *.wgdfa
│   │   └── eflomal            # files obtained from eflomal 
│   │       └── .wgdfa
│   └── dropout_bpe
│       ├── segmentations
│       │   └── *.bpe
│       ├── fastalign
│       │   └── *.wgdfa
│       └── eflomal
├── doc                        # LaTeX files for the writing of the thesis
│   ├── figures
│   ├── sections
│   └── *.tex files
├── reports
│   ├── scores_normal_bpe      # scores for BPE
│   │   └── *.csv, *.png
│   └── scores_dropout_bpe     # scores for BPE dropout space/no space, and depending on dropout rate
│       ├── space
│       │   ├── 0.1
│       │   └── 0.2
│       |       └── *.csv, *.png
│       └── no space
│           └── 0.1
│               └── *.csv, *.png
├── src                        # python files
│   ├── learn_bpe.py
│   ├── apply_bpe.py
│   ├── extract_alignments.py
│   └── calc_align_score.py
├── tools                        # fastalign, eflomal installation directories
│   ├── fastalign
│   └── eflomal
├── .gitignore
├── README.md
├── requirements.txt
└── settings.py
```
