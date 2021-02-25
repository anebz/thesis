#!/usr/bin/env python3
import os
import ray
import sys
import time
import codecs
from tqdm import tqdm
from datetime import timedelta

from learn_bpe import learn_bpe, read_corpus, join_best_mappings, write_bpe
from apply_bpe import apply_bpe, apply_bpe_fancy
from extract_alignments import extract_alignments

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from settings import *

def learn_bpes(lang):

    modelpath = join(inputdir, f"{lang}{'' if params[lang]['space'] else '_ns'}{'_'+str(it) if it >= 0 else ''}.model")
    if os.path.isfile(modelpath):
        print(f"Importing bpe_model for lang:{lang}, file:{modelpath}")
        bpe_model = [tuple(line.strip('\r\n ').split()) for line in codecs.open(modelpath, encoding='utf-8')][1:]
        return bpe_model

    corpus = read_corpus(lang, codecs.open(inputpath[lang], encoding='utf-8'))
    corpus = join_best_mappings(lang, '\n'.join(corpus))
    bpe_model = learn_bpe(lang, corpus, learn_vocab_size)
    write_bpe(lang, bpe_model)
    return bpe_model


@ray.remote
def bpe_pipeline(corpusfile, bpe_model_target, corpus_target, i):
    print("apply_bpe ", i)
    apply_bpe(target, bpe_model_target, corpus_target, i)
    print("extract aligns ", i)
    for vocab_size in merges:
        extract_alignments(corpusfile, vocab_size, i)
    print("done ", i)
    return


@ray.remote
def bpe_pipeline_fancy(corpusfile, bpe_model_target, corpus_target, vocab_size, i):
    print("apply_bpe ", i)
    apply_bpe_fancy(target, bpe_model_target, corpus_target, vocab_size, i)
    print("extract aligns ", i)
    extract_alignments(corpusfile, vocab_size, i)
    print("done ", i)
    return


if __name__ == "__main__":

    print(f"Running iteration {it}")
    bpe_model_target = learn_bpes(target)
    corpus_source = [line.strip('\r\n ').split('\t')[1] for line in codecs.open(inputpath[source])]
    corpus_target = read_corpus(target, codecs.open(inputpath[target], encoding='utf-8'))

    
    t0 = time.time()
    ray.init(num_cpus=5)
    '''
    futures = [bpe_pipeline.remote(corpus_source, bpe_model_target, corpus_target, i) for i in range(dropout_samples)]
    ray.get(futures)
    '''
    for vocab_size in merges:
        corpus_target = join_best_mappings(target, corpus_target, vocab_size/max_it)
        futures = [bpe_pipeline_fancy.remote(corpus_source, bpe_model_target, corpus_target, vocab_size, i) for i in range(dropout_samples)]
        ray.get(futures)
    ray.shutdown()

    print(f"The pipeline took {str(timedelta(seconds=time.time()-t0))}")
