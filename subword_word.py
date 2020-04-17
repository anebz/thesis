import os
import glob
import codecs
import inspect

def map_subword_to_word(corpus):
    '''
    Input: list of sentences with subword separation
        [
            '_We _do _no t _be li eve _.',
            '_Thi s _is _a _sent ence _.',
            ...
        ]
    Output: list of vectors pointing to which word each subword belongs to
        [
            [0, 1, 2, 2, 3, 3, 3, 4],
            [0, 0, 1, 2, 3, 4, 5],
            ...
        ]
    '''
    worded_corpus = []
    for sent in corpus:
        sent = sent.split()
        subwords = [0]
        i = 0
        for subw in sent[1:]:
            if subw[0] == u'\u2581':
                i += 1
            subwords.append(i)
        worded_corpus.append(subwords)
    return worded_corpus


if __name__ == "__main__":
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    datapath = os.path.join(currentdir, 'data')

    os.chdir(datapath)
    for ifile in glob.glob("*.bpe"):

        argsinput = codecs.open(ifile, encoding='utf-8').readlines()
        worded_corpus = map_subword_to_word(argsinput)
