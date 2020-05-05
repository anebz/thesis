import os
import codecs
import random
import inspect
import pandas as pd

from calc_align_score import load_gold, calc_score, plot_scores

def get_baseline_score(currentdir):
    gold_path = os.path.join(currentdir, 'pbc_utils/data/eng_deu/eng_deu.gold')
    alfile = os.path.join(currentdir, 'data/fastalign/input.gdfa')
    probs, surs, surs_count = load_gold(gold_path)

    scores = []
    score = [0]
    score.extend(list(calc_score(alfile, probs, surs, surs_count)))
    scores.append(score)
    baseline_df = pd.DataFrame(scores, columns=['num_symbols', 'prec', 'rec', 'f1', 'AER'])
    return baseline_df

if __name__ == "__main__":
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    datapath = os.path.join(currentdir, 'data/test_scores')
    os.chdir(datapath)

    avgs = [3, 5, 7, 10]
    for i in avgs:

        # get random i indexes
        random_idx = set()
        while len(random_idx) < i:
            random_idx.add(random.randrange(10))

        # baseline score
        baseline_df = get_baseline_score(currentdir)
        df = pd.DataFrame()

        for rd_idx in list(random_idx):

            df2 = pd.read_csv(os.path.join(datapath, 'scores_'+str(rd_idx)+'.csv'))

            # first step of the iteration, just get the whole dataframe
            if df.empty:
                df = df2
                continue
            
            for col in list(df2)[1:]:
                df[col] += df2[col]
        
        # divide all by \# elements added, to get average
        for col in list(df)[1:]:
            df[col] = df[col].apply(lambda x: x/i)
    
        df = pd.concat([baseline_df, df])

        plot_name = 'scores_avg_'+str(i)
        plot_scores(df, datapath+'/avg', plot_name)
        df.to_csv(os.path.join(datapath+'/avg', plot_name+'.csv'), index=False)
