import os
from os.path import join
import sys
import copy
import codecs
import pandas as pd
from tqdm import tqdm
from collections import Counter

# import global variables from settings.py
from settings import *
from calc_align_score import *


def merge_dropout_alignments():
    union_merge, inter_merge, thres_merge = {}, {}, {}

    os.chdir(join(bpedir, 'fastalign'))
    for num_symbols in tqdm(all_symbols, desc=f"merge_dropout: num_symbols={all_symbols}, union, inter, thres"):
        union_merge[num_symbols], inter_merge[num_symbols], thres_merge[num_symbols] = [], [], []

        for i in range(dropout_repetitions):

            for j, line in enumerate(open(str(num_symbols)+'_'+str(i)+'.wgdfa', 'r').readlines()):
                al = frozenset(line.strip().split("\t")[1].split())

                # at the first iteration, just append the alignment
                if i == 0:
                    union_merge[num_symbols].append(al)
                    inter_merge[num_symbols].append(al)
                    thres_merge[num_symbols].append(Counter(al))
                    continue
                
                # do union, intersection or frequency addition
                union_merge[num_symbols][j] |= al
                inter_merge[num_symbols][j] &= al
                thres_merge[num_symbols][j] += Counter(al)

        # write to output
        unionfile = codecs.open(str(num_symbols)+'_union.wgdfa', 'w')
        interfile = codecs.open(str(num_symbols)+'_inter.wgdfa', 'w')
        thresfiles = {merge_t: codecs.open(str(num_symbols)+'_thres_'+str(merge_t)+'.wgdfa', 'w') for merge_t in merge_threshold}

        for i in range(len(union_merge[num_symbols])):
            unionfile.write(f"{i}\t{' '.join(union_merge[num_symbols][i])}\n")
            interfile.write(f"{i}\t{' '.join(inter_merge[num_symbols][i])}\n")

            # get alignments more common than the merge_threshold %
            for merge_t in merge_threshold:
                common_aligns = [k for k in thres_merge[num_symbols][i] 
                                if thres_merge[num_symbols][i][k] > merge_t * dropout_repetitions]
                thresfiles[merge_t].write(f"{i}\t{' '.join(common_aligns)}\n")
    return


def calc_score_merges():
    probs, surs, surs_count = load_gold(goldpath)
    baseline_df = pd.read_csv(join(datadir, 'normal_bpe/scores/scores_'+source+'_'+target+'.csv'))
    for merge_type in ['union', 'inter']:
        scores = []
        for num_symbols in all_symbols:
            mergefilepath = join(bpedir, 'fastalign', str(num_symbols)+'_'+merge_type+'.wgdfa')

            score = [int(num_symbols)]
            score.extend(list(calc_score(mergefilepath, probs, surs, surs_count)))
            scores.append(score)

       	df = pd.DataFrame(scores, columns=['num_symbols', 'prec', 'rec', 'f1', 'AER']).round(decimals=3)
        scoredir = join(bpedir, 'scores', 'scores') + ('_ns' if not space else '') + '_' + merge_type
        
        print(f"Scores saved into {scoredir}")
        df.to_csv(scoredir+'.csv', index=False)
        plot_scores(df, baseline_df, scoredir)

    # threshold case, iterate all merge_threshold|saved
    for merge_t in merge_threshold:
        scores = []
        for num_symbols in all_symbols:
            mergefilepath = join(bpedir, 'fastalign', str(num_symbols)+'_thres_'+str(merge_t)+'.wgdfa')

            score = [int(num_symbols)]
            score.extend(list(calc_score(mergefilepath, probs, surs, surs_count)))
            scores.append(score)

        df = pd.DataFrame(scores, columns=['num_symbols', 'prec', 'rec', 'f1', 'AER']).round(decimals=3)
        scoredir = join(bpedir, 'scores', 'scores') + ('_ns' if not space else '') + '_' + str(merge_t) + '_thres'
        
        print(f"Scores saved into {scoredir}")
        df.to_csv(scoredir+'.csv', index=False)
        plot_scores(df, baseline_df, scoredir)
    return


if __name__ == "__main__":
    merge_dropout_alignments()
    calc_score_merges()
