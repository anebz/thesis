import os
import inspect
import codecs

if __name__ == "__main__":
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    datadir = os.path.join(currentdir, 'test')
    os.chdir(datadir)

    all_symbols = [100, 500, 1000, 2000, 4000, 8000]
    langs = ['eng', 'deu']

    for lang in langs:
        outfile = os.path.join(datadir, 'merged', 'merged_'+lang+'_'+str(len(all_symbols))+'.bpe')
        merged_file = codecs.open(outfile, 'w', encoding='utf-8')

        for i, symb in enumerate(all_symbols):
            infile = os.path.join(datadir, lang+'_'+str(symb)+'_'+str(i)+'.bpe')
            incontent = codecs.open(infile, 'r', encoding='utf-8').read()
            merged_file.write(incontent)
