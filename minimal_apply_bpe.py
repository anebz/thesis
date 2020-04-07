# minimal BPE from arxiv 1508.07909
# to apply at test time

import os
import re
import inspect
import codecs

def apply_bpe(argsinput, codes, argsoutput, merges):
    
    # from paper's code
    bpe_merges = [tuple(item.strip('\r\n ').split(' ')) for (n, item) in enumerate(codes) if n < merges]
    #bpe_codes_reverse = dict([(pair[0] + pair[1], pair) for pair, i in bpe_codes.items()])

    '''
    for bigram in merges:
        for sent in corpus:
            if bigram in sent: # you can make a set of available bigrams for each sentence and update them.
                apply_merge(sent, bigram) # update the bigram set for the sentence

    The second way is to look at the merge list as a list of BPEs ('th e' -> 'the').
    Now, you start from the largest BPE and find which BPE you can find in sentences. 
    Then you find smaller BPEs for the rest of the characters.
    '''

    # read corpus into list of list of bigram tuples
    corpus = []
    for line in argsinput:
        all_line = []
        _, line = line.split('\t')
        for word in line.strip('\r\n ').split(' '):
            word_splitted = (u'\u2581' + word[0],) + tuple(word[1:])

            # save bigrams
            if len(word_splitted) > 2:
                all_word = []
                prev_char = word_splitted[0]
                for letter in word_splitted[1:]:
                    all_word.append((prev_char, letter))
                    prev_char = letter
            else:
                all_word = [word_splitted]
            all_line.append(all_word)
        corpus.append(all_line)

    return


if __name__ == "__main__":
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    argsinput = codecs.open(os.path.join(currentdir, 'data/eng_with_10k.txt'), encoding='utf-8')
    codes = codecs.open(os.path.join(currentdir, 'data/minimal_model.bpe'), encoding='utf-8')
    argsoutput = codecs.open(os.path.join(currentdir, 'data/eng_merged.txt'), 'w', encoding='utf-8')
    merges = 100
    codes.seek(0)

    apply_bpe(argsinput, codes, argsoutput, merges)
