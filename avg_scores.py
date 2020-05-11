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
        baseline_df = get_baseline_score()
        df = pd.DataFrame()

        for rd_idx in list(random_idx):

            df2 = pd.read_csv(os.path.join(bpepath, 'scores', 'scores_'+str(rd_idx)+'.csv'))

            # first step of the iteration, just get the whole dataframe
            if df.empty:
                df = df2
                continue
            
            for col in list(df2)[1:]:
                df[col] += df2[col]
        
        # divide all by \# elements added, to get average
        for col in list(df)[1:]:
            df[col] = df[col].apply(lambda x: x/i)
    
        df = pd.concat([baseline_df, df]).round(decimals=3)

        plot_name = 'scores/avg/scores_avg_'+str(i)
        df.to_csv(os.path.join(bpepath, plot_name+'.csv'), index=False)
        plot_scores(df, join(bpepath, plot_name))
