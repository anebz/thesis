#!/usr/bin/env python3
import os
import ray
import sys
import time
import codecs
from tqdm import tqdm
from datetime import timedelta

from learn_bpe import learn_bpe, read_corpus, write_bpe
from apply_bpe import apply_bpe
from extract_alignments import extract_alignments

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from settings import *

def learn_bpes(lang):

    if not params[lang]['bpe']:
        print(f"Language {lang} doesn't have the BPE mode activated")
        return None

    modelpath = join(inputdir, f"{lang}{'' if params[lang]['space'] else '_ns'}{'_'+str(it) if it >= 0 else ''}.model")
    _vocab_size = learn_vocab_size
    if os.path.isfile(modelpath):
        print(f"Importing bpe_model for lang:{lang}, file:{modelpath}")
        bpe_model = [tuple(line.strip('\r\n ').split()) for line in codecs.open(modelpath, encoding='utf-8')]
        _vocab_size = int(bpe_model[0][1])
        # the vocabulary size is already existent in the bpe_model
        if learn_vocab_size <= _vocab_size:
            return bpe_model[1:]
    
    corpus = read_corpus(lang, codecs.open(inputpath[lang], encoding='utf-8'))

    # if a vocab of 30k should be created but a vocab of 10k already exists, merge the first 10k units of the vocab
    if learn_vocab_size > _vocab_size:
        vocab_to_learn = learn_vocab_size - _vocab_size
        corpus = '\n'.join(corpus)
        print(f"Reusing {_vocab_size} symbols from the BPE model found")
        for bigram in tqdm(bpe_model[1:]):
            corpus = corpus.replace(' '.join(bigram), ''.join(bigram))
        corpus = corpus.split('\n')
    else:
        vocab_to_learn = learn_vocab_size
    
    most_freq_merges = learn_bpe(lang, corpus, vocab_to_learn)

    # update the list of most freq merges for both cases
    if learn_vocab_size > _vocab_size:
        most_freq_merges = bpe_model[1:] + most_freq_merges

    write_bpe(lang, most_freq_merges)

    return most_freq_merges


@ray.remote
def bpe_pipeline(corpusfile, bpe_model_target, i):
    print("apply_bpe ", i)
    corpus_target = read_corpus(target, codecs.open(inputpath[target], encoding='utf-8'))
    target_bpe = apply_bpe(target, bpe_model_target, corpus_target, i)
    print("extract aligns ", i)
    extract_alignments(corpusfile, i)
    print("done ", i)
    return


if __name__ == "__main__":

    print(f"Running iteration {it}")

    os.makedirs(join(bpedir, 'segmentations'), exist_ok=True)
    os.makedirs(join(bpedir, 'fastalign'), exist_ok=True)

    bpe_model_target = learn_bpes(target)
    corpus_source = [line.strip('\r\n ').split('\t')[1] for line in codecs.open(inputpath[source])]

    t0 = time.time()
    ray.init(num_cpus=5)
    futures = [bpe_pipeline.remote(corpus_source, bpe_model_target, i) for i in range(dropout_samples)]
    ray.get(futures)
    ray.shutdown()

    print(f"The pipeline took {str(timedelta(seconds=time.time()-t0))}")
