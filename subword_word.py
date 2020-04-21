import os
import glob
import codecs
import inspect

def map_subword_to_word(corpus, bpes, lang):
    '''
    Input: list of sentences with subword separation
        [
            '_We _do _no t _be li eve _.',
            '_Thi s _is _a _sent ence _.',
            ...
        ]
    Output: dictionary of each language and 
    a list of vectors pointing to which word each subword belongs to
        {
            'eng':
            [
                [0, 1, 2, 2, 3, 3, 3, 4],
                [0, 0, 1, 2, 3, 4, 5],
                ...
            ],
            'deu':
            [
                [0, 1, 2, 3, 3, 4, 4, 5],
                [0, 0, 1, 1, 2, 3, 4],
                ...
            ],
        }
        
    '''
    if lang in bpes:
        return bpes
    bpes[lang] = []
    for sent in corpus:
        sent = sent.split()
        subwords = [0]
        i = 0
        for subw in sent[1:]:
            if subw[0] == u'\u2581':
                i += 1
            subwords.append(i)
        bpes[lang].append(subwords)
    return bpes


def bpe_word_align(bpes, bpe_aligns):
    '''
    Input: dictionary of bpes obtained as output of map_subword_to_word()
    Output: list of word alignments and their indexes
        "
            0   0-0 0-1 1-1 1-2 3-1 2-4 \n
            1   0-0 1-0 1-1 2-1 \n
            ...
        "
    '''
    all_word_aligns = ''
    # iterate all sentences
    i = 0
    for sent1, sent2, bpe_al in zip(bpes['eng'], bpes['deu'], bpe_aligns):
        word_aligns = ''
        # iterate each alignment
        # bpe_al.split('\t')[1] to remove the index in the alignment file .gdfa
        for al in bpe_al.split('\t')[1].split():
            firstal, secondal = al.split('-')
            new_al = str(sent1[int(firstal)]) + '-' + str(sent2[int(secondal)])
            # skip already seen word alignments
            if not new_al in word_aligns:
                word_aligns += new_al + ' '
        all_word_aligns += str(i) + "\t" + word_aligns[:-1] + "\n"
        i += 1
    return all_word_aligns


if __name__ == "__main__":
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    datapath = os.path.join(currentdir, 'data')

    os.chdir(datapath)
    for alfile in glob.glob("fastalign/[0-9]*.gdfa"):
        num_symbols = alfile.split(".")[0].split("/")[1]
        bpes = {}
        for ifile in glob.glob("*_"+num_symbols+".bpe"):
            lang, _ = ifile.split('.')[0].split('_')
            argsinput = codecs.open(ifile, encoding='utf-8')
            bpes = map_subword_to_word(argsinput, bpes, lang)

        argsalign = codecs.open(alfile, encoding='utf-8')
        all_word_aligns = bpe_word_align(bpes, argsalign)

        argsoutput = codecs.open(os.path.join(datapath, 'fastalign', num_symbols+'_word.gdfa'), 'w', encoding='utf-8')
        argsoutput.write(all_word_aligns)
