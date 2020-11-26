#!/usr/bin/env python3
import os
import ray
import sys
import time
import codecs
from datetime import timedelta

from learn_bpe import learn_bpe, read_corpus, write_bpe
from apply_bpe import apply_bpe, create_parallel_text
from extract_alignments import extract_alignments
from find_bpe import aggregate_mappings

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from settings import *

def learn_bpes(lang):
    modelpath = join(inputdir, f"{lang}{'' if params[lang]['space'] else '_ns'}{'_'+str(it) if it >= 0 else ''}.model")
    if os.path.isfile(modelpath):
        print(f"Importing bpe_model for lang:{lang}")
        bpe_model = [tuple(line.strip('\r\n ').split()) for line in codecs.open(modelpath, encoding='utf-8').readlines()[1:]]
        return bpe_model
        
    if not params[lang]['bpe']:
        print(f"Language {lang} doesn't have the BPE mode activated")
        return None

    corpusfile = codecs.open(inputpath[lang], encoding='utf-8').readlines()
    most_freq_merges = learn_bpe(lang, corpusfile)
    write_bpe(lang, most_freq_merges)
    return most_freq_merges


def apply_bpes(corpus_source, bpe_model_target, i):
    corpusfile = codecs.open(inputpath[target], encoding='utf-8').readlines()
    corpus_target = read_corpus(target, corpusfile)
    target_bpe = apply_bpe(target, bpe_model_target, corpus_target, i)

    create_parallel_text(corpus_target, target_bpe.split('\n'))
    return

@ray.remote
def bpe_pipeline(corpus_source, bpe_model_target, i):
    print("apply_bpe ", i)
    apply_bpes(corpus_source, bpe_model_target, i)
    print("extract aligns ", i)
    extract_alignments(i)
    print("done ", i)
    return


if __name__ == "__main__":

    os.makedirs(join(bpedir, 'segmentations'), exist_ok=True)
    os.makedirs(join(bpedir, 'fastalign'), exist_ok=True)

    corpusfile = codecs.open(inputpath[source], encoding='utf-8').readlines()
    corpus_source = read_corpus(source, corpusfile)
    bpe_model_target = learn_bpes(target)
    
    t0 = time.time()
    ray.init()
    futures = [bpe_pipeline.remote(corpus_source, bpe_model_target, i) for i in range(dropout_samples)]
    ray.get(futures)

    print(f"The pipeline took {str(timedelta(seconds=time.time()-t0))}")
