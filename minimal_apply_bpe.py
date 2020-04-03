# minimal BPE from arxiv 1508.07909
# to apply at test time

import os
import re
import inspect
import codecs

def main():
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    argsinput = codecs.open(os.path.join(currentdir, 'data/eng_with_10k.txt'), encoding='utf-8')
    codes = codecs.open(os.path.join(currentdir, 'data/minimal_model.bpe'), encoding='utf-8')
    argsoutput = codecs.open(os.path.join(currentdir, 'data/eng_merged.txt'), 'w', encoding='utf-8')
    merges = 100

    codes.seek(0)
    # check version information
    bpe_codes = [tuple(item.strip('\r\n ').split(' ')) for (n, item) in enumerate(codes) if (n < merges or merges == -1)]
    bpe_codes = dict([(code, i) for (i, code) in reversed(list(enumerate(bpe_codes)))])
    bpe_codes_reverse = dict([(pair[0] + pair[1], pair) for pair, i in bpe_codes.items()])

    for line in argsinput:
        pass


if __name__ == "__main__":
    main()
