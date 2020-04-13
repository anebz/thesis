# minimal BPE from arxiv 1508.07909
# to apply at test time

import os
import re
import codecs
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
        line = line.strip('\r\n. ').split(' ') if line.strip('\r\n. ') else []
        if line: # ignore empty lines, or lines with just a .
            for word in line:
                if not word:
                    continue
                # add '_' to beginning of each word
                newword = [u'\u2581' + word[0]]
                newword.extend(list(word[1:]))
                corpus.extend(newword)
            corpus.append('\n')
    return corpus


def merge_corpus(corpus, bpe_merges, argsoutput):
    '''
    merge the bigrams found in the corpus iteratively
    Inputs: 
    * corpus in the style from read_corpus
    * bpe_merges read from the input file
    Output:
    * Merged corpus written into `argsoutput`
    '''

    merged_corpus = corpus.copy()
    for bigram in tqdm(bpe_merges):
        pattern = re.compile(r'(?<!\S)' + re.escape(' '.join(bigram)) + r'(?!\S)')
        pair_str = ''.join(bigram).replace('\\', '\\\\')

        # expand into a big string
        new_word = ' '.join(merged_corpus)
        # merge bigram
        new_word = pattern.sub(pair_str, new_word)
        # join again
        merged_corpus = list(new_word.split(' '))

    # restore corpus and write to output
    restored_corpus = ' '.join(merged_corpus)
    restored_corpus = restored_corpus.replace(u'\u2581', '').replace(' \n ', '\n')
    argsoutput.write(restored_corpus)
    
    return 


def apply_bpe(argsinput, codes, argsoutput):

    bpe_merges = [tuple(item.strip('\r\n ').split(' ')) for (n, item) in enumerate(codes)]

    corpus = read_corpus(argsinput)

    merge_corpus(corpus, bpe_merges, argsoutput)

    return


if __name__ == "__main__":
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    datapath = os.path.join(currentdir, 'data')

    lang = 'deu' # eng, deu
    numsymbols = '2500' # 250, 2500

    argsinput = codecs.open(os.path.join(datapath, 'input/'+lang+'_with_10k.txt'), encoding='utf-8')
    codes = codecs.open(os.path.join(datapath, lang+'_model_'+numsymbols+'.bpe'), encoding='utf-8')
    argsoutput = codecs.open(os.path.join(datapath, lang+'_merged_'+numsymbols+'.txt'), 'w', encoding='utf-8')

    print("Merging BPE symbols for {}".format(lang))
    time0 = datetime.datetime.now().replace(microsecond=0)

    apply_bpe(argsinput, codes, argsoutput)
    
    time1 = datetime.datetime.now().replace(microsecond=0)
    print("Time elapsed:", time1-time0)
