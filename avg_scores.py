import os
import codecs
import random
import pandas as pd

from calc_align_score import *
# import global variables from lib/__init__.py
from lib import *


if __name__ == "__main__":

    avgs = [3, 5, 7, 10]
    for i in avgs:

        # get random i indexes
        random_idx = set()
        while len(random_idx) < i:
            random_idx.add(random.randrange(10))

        # baseline score
        if dropout:
            baseline_df = pd.read_csv(join(datadir, 'normal_bpe/scores/scores_'+source+'_'+target+'.csv'))
        else:
            gold_path = join(datadir, 'input/eng_deu.gold')
            baseline_df = get_baseline_score(*load_gold(gold_path))

        df = pd.DataFrame()

        for rd_idx in list(random_idx):

            df2 = pd.read_csv(os.path.join(bpedir, 'scores', 'scores_'+str(rd_idx)+'.csv'))

            # first step of the iteration, just get the whole dataframe
            if df.empty:
                df = df2
                continue
            
            for col in list(df2)[1:]:
                df[col] += df2[col]
        
        # divide all by \# elements added, to get average
        for col in list(df)[1:]:
            df[col] = df[col].apply(lambda x: x/i)

        plot_name = 'scores/avg/scores_avg_'+str(i)
        df.round(decimals=3).to_csv(os.path.join(bpedir, plot_name+'.csv'), index=False)
        plot_scores(df, baseline_df, join(bpedir, plot_name))
