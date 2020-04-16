# minimal BPE from arxiv 1508.07909
# to apply at test time

import os
import re
import glob
import codecs
import random
import inspect
import datetime
from tqdm import tqdm

def read_corpus(argsinput):
    '''
    read corpus into list of list of bigram tuples
    Input: argsinput
    Output:
        [
            '_W', 'e',
            '_d'. 'o',
            '_n', 'o', 't',
            '_b', 'e', 'l', 'i', 'e', 'v', 'e',
            ...
            '\n',
            ...
        ]
    '''

    corpus = []
    for line in argsinput:
        # split the number found in the line
        _, line = line.split('\t')
        line = line.strip('\r\n ').split(' ') if line.strip('\r\n ') else []
        for word in line:
            # add '_' to beginning of each word
            newword = [u'\u2581' + word[0]]
            newword.extend(list(word[1:]))
            corpus.extend(newword)
        corpus.append('\n')
    return corpus


def merge_corpus(corpus, bpe_merges, dropout=0.1):
    '''
    merge the bigrams found in the corpus iteratively
    Inputs: 
    * corpus in the style from read_corpus
    * bpe_merges read from the input file
    Output:
    * Merged corpus written into `argsoutput`
    '''

    # expand into a big string
    str_corpus = ' '.join(corpus)

    # iterate bpe merges
    for bigram in tqdm(bpe_merges):

        if random.uniform(0, 1) < dropout:
            continue

        pattern = re.compile(r'(?<!\S)' + re.escape(' '.join(bigram)) + r'(?!\S)')

        # merge bigram
        str_corpus = pattern.sub(''.join(bigram), str_corpus)
    
    return str_corpus.replace(' \n ', '\n')


if __name__ == "__main__":
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    datapath = os.path.join(currentdir, 'data')

    dropout = 0.1

    os.chdir(datapath)
    for ifile in glob.glob("*.model"):
        lang = ifile.split('.')[0]
        codes = codecs.open(os.path.join(datapath, lang+'.model'), encoding='utf-8').readlines()
        _, num_symbols = codes.pop(0).split()

        argsinput = codecs.open(os.path.join(datapath, 'input/'+lang+'_with_10k.txt'), encoding='utf-8')
        argsoutput = codecs.open(os.path.join(datapath, lang+'_'+str(num_symbols)+'.bpe'), 'w', encoding='utf-8')

        print("Merging BPE symbols for {}".format(lang))
        time0 = datetime.datetime.now().replace(microsecond=0)

        ''' apply BPE '''
        corpus = read_corpus(argsinput)
        bpe_merges = [tuple(item.strip('\r\n ').split(' ')) for (n, item) in enumerate(codes)]
        merged_corpus = merge_corpus(corpus, bpe_merges, dropout)
        argsoutput.write(merged_corpus)

        time1 = datetime.datetime.now().replace(microsecond=0)
        print("Time elapsed:", time1-time0)
