import os
import sys
import glob
import codecs
import random
import inspect
from tqdm import tqdm


def read_corpus(argsinput):
    '''
    read corpus into list of list of bigram tuples
    Input: argsinput
        [
            '1   This is the first line',
            '2   The second line',
            ....
        ]
    Output:
        [
            '_W', 'e',
            '_d', 'o',
            '_n', 'o', 't',
            '_b', 'e', 'l', 'i', 'e', 'v', 'e',
            ...
            '\n',
            ...
        ]
    '''

    corpus = []
    for line in argsinput:
        # line.split('\t')[1] to strip the number in the line
        line = line.split('\t')[1].strip('\r\n ').split(' ')
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
    * Merged corpus
    '''

    str_corpus = ' '.join(corpus)
    for bigram in tqdm(bpe_merges):

        '''
        if random.uniform(0, 1) < dropout:
            continue
        '''
        # merge bigram
        str_corpus = str_corpus.replace(' '.join(bigram), ''.join(bigram))
    
    return str_corpus.replace(' \n ', '\n')


if __name__ == "__main__":
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    datapath = os.path.join(currentdir, 'data')

    dropout = 0.1
    all_symbols = [1000, 2000, 3000, 4000, 8000]

    os.chdir(datapath)
    for num_symbols in all_symbols:
        for ifile in glob.glob("*.model"):

            # open BPE model
            lang = ifile.split('.')[0]
            bpe_model = codecs.open(ifile, encoding='utf-8').readlines()
            model_symbols = bpe_model[0].strip('\r\n').split()[1]

            if num_symbols > int(model_symbols):
                print(f"Asking for {num_symbols} but the BPE model only has {model_symbols}")
                sys.exit()
            
            # only get the desired amount of symbols
            bpe_model = bpe_model[1:num_symbols+1]

            argsinput = codecs.open(os.path.join(datapath, 'input/'+lang+'_with_10k.txt'), encoding='utf-8')

            print(f"Merging BPE symbols for {lang} and {num_symbols} symbols")

            ''' apply BPE '''
            corpus = read_corpus(argsinput)
            bpe_merges = [tuple(item.strip('\r\n ').split(' ')) for (n, item) in enumerate(bpe_model)]
            merged_corpus = merge_corpus(corpus, bpe_merges, dropout)

            # write to output
            argsoutput = codecs.open(os.path.join(datapath, lang+'_'+str(num_symbols)+'.bpe'), 'w', encoding='utf-8')
            argsoutput.write(merged_corpus)
