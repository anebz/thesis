import os
import glob
import codecs
import random
import inspect
import pandas as pd

from calc_align_score import load_gold, calc_score, plot_scores

if __name__ == "__main__":
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    datapath = os.path.join(currentdir, 'data/test_scores')
    os.chdir(datapath)

    avgs = [3, 5, 7, 10]
    for i in avgs:

        df = pd.DataFrame()
        '''
        # baseline score
        gold_path = os.path.join(currentdir, 'pbc_utils/data/eng_deu/eng_deu.gold')
        probs, surs, surs_count = load_gold(gold_path)

        scores = []
        alfile = os.path.join(datapath, 'fastalign/input.gdfa')
        score = [0]
        score.extend(list(calc_score(alfile, probs, surs, surs_count)))
        scores.append(score)
       	df = pd.DataFrame(scores, columns=['num_symbols', 'prec', 'rec', 'f1', 'AER'])
        '''

        for alfile in glob.glob("*.csv"):

            if random.uniform(0, 10) > i:
                continue

            # read score .csv and average
            df2 = pd.read_csv(alfile)
            for col in list(df2)[1:]:
                df2[col] = df2[col].apply(lambda x: x/i)
            

            if df.empty:
                df = df2
                continue
            
            for col in list(df)[1:]:
                df[col] = df[col] + df2[col]

        plot_name = 'scores_avg_'+str(i)
        plot_scores(df, datapath+'/avg', plot_name)
        df.to_csv(os.path.join(datapath+'/avg', plot_name+'.csv'), index=False)
