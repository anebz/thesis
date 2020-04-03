# minimal BPE from arxiv 1508.07909
# to apply at test time

import os
import re
import inspect
import codecs

def apply_bpe(argsinput, codes, argsoutput, merges):
    
    # from paper's code
    bpe_codes = [tuple(item.strip('\r\n ').split(' ')) for (n, item) in enumerate(codes) if (n < merges or merges == -1)]
    bpe_codes = dict([(code, i) for (i, code) in reversed(list(enumerate(bpe_codes)))])
    bpe_codes_reverse = dict([(pair[0] + pair[1], pair) for pair, i in bpe_codes.items()])

    '''
    for bigram in merges:
        for sent in corpus:
            if bigram in sent: # you can make a set of available bigrams for each sentence and update them.
                apply_merge(sent, bigram) # update the bigram set for the sentence

    The second way is to look at the merge list as a list of BPEs ('th e' -> 'the').
    Now, you start from the largest BPE and find which BPE you can find in sentences. 
    Then you find smaller BPEs for the rest of the characters.
    '''

    for line in argsinput:
        _, line = line.split('\t')
        all_line = []
        for word in line.strip('\r\n ').split(' '):
            word_splitted = (u'\u2581' + word[0],) + tuple(word[1:])
            all_line.append(word_splitted)

    return


if __name__ == "__main__":
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    argsinput = codecs.open(os.path.join(currentdir, 'data/eng_with_10k.txt'), encoding='utf-8')
    codes = codecs.open(os.path.join(currentdir, 'data/minimal_model.bpe'), encoding='utf-8')
    argsoutput = codecs.open(os.path.join(currentdir, 'data/eng_merged.txt'), 'w', encoding='utf-8')
    merges = 100
    codes.seek(0)

    apply_bpe(argsinput, codes, argsoutput, merges)
