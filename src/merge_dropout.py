import os
from os.path import join
import sys
import codecs
import pandas as pd
from tqdm import tqdm
from collections import Counter

# import global variables from settings.py
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from settings import *
from calc_align_score import *


def merge_dropout_alignments():
    union_merge, inter_merge, thres_merge = {}, {}, {}

    os.chdir(join(bpedir, mode))
    for num_symbols in tqdm(all_symbols, desc=f"merge_dropout: dropout={dropout}, union, inter, thres"):
        union_merge[num_symbols], inter_merge[num_symbols], thres_merge[num_symbols] = [], [], []

        for i in range(dropout_samples):

            alpath = join(bpedir, mode, f"{num_symbols}_{i}{'_'+source if source_bpe else ''}{'_'+target if target_bpe else ''}.wgdfa")
            alfile = open(alpath, 'r').readlines()
            for j, line in enumerate(alfile):
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
        unionfile = codecs.open(f'{num_symbols}_union.wgdfa', 'w')
        interfile = codecs.open(f'{num_symbols}_inter.wgdfa', 'w')
        thresfiles = {merge_t: codecs.open(f'{num_symbols}_thres_{merge_t}.wgdfa', 'w') for merge_t in merge_threshold}

        for i in range(len(union_merge[num_symbols])):
            unionfile.write(f"{i}\t{' '.join(union_merge[num_symbols][i])}\n")
            interfile.write(f"{i}\t{' '.join(inter_merge[num_symbols][i])}\n")

            # get alignments more common than the merge_threshold %
            for merge_t in merge_threshold:
                common_aligns = [k for k in thres_merge[num_symbols][i] 
                                if thres_merge[num_symbols][i][k] > merge_t * dropout_samples]
                thresfiles[merge_t].write(f"{i}\t{' '.join(common_aligns)}\n")
    return


def calc_score_merges():
    probs, surs, surs_count = load_gold(goldpath)
    baseline_df = pd.read_csv(join(baselinedir, f"{source}_{target}{'' if space else '_ns'}_{mode}.csv"))
    scorespath = join(scoredir, 'space' if space else 'no space', str(dropout))
    os.makedirs(scorespath, exist_ok=True)
    for merge_type in ['union', 'inter']:
        scores = []
        for num_symbols in all_symbols:
            mergefilepath = join(bpedir, mode, f'{num_symbols}_{merge_type}.wgdfa')

            score = [int(num_symbols)]
            score.extend(list(calc_score(mergefilepath, probs, surs, surs_count)))
            scores.append(score)

       	df = pd.DataFrame(scores, columns=['num_symbols', 'prec', 'rec', 'f1', 'AER']).round(decimals=3)
        scorename = join(scorespath, f"{source}_{target}_{''if space else 'ns_'}{merge_type}_{mode}{'_'+source if source_bpe else ''}{'_'+target if target_bpe else ''}")

        print(f"Scores saved into {scorename}")
        df.to_csv(scorename+'.csv', index=False)
        plot_scores(df, baseline_df, scorename)

    # threshold case, iterate all merge_thresholds saved
    for merge_t in merge_threshold:
        scores = []
        for num_symbols in all_symbols:
            mergefilepath = join(bpedir, mode, f'{num_symbols}_thres_{merge_t}.wgdfa')

            score = [int(num_symbols)]
            score.extend(list(calc_score(mergefilepath, probs, surs, surs_count)))
            scores.append(score)

        df = pd.DataFrame(scores, columns=['num_symbols', 'prec', 'rec', 'f1', 'AER']).round(decimals=3)
        scorename = join(scorespath, f"{source}_{target}_{'' if space else 'ns_'}{merge_t}_thres_{mode}{'_'+source if source_bpe else ''}{'_'+target if target_bpe else ''}")
        
        print(f"Scores saved into {scorename}")
        df.to_csv(scorename+'.csv', index=False)
        plot_scores(df, baseline_df, scorename)
    return


if __name__ == "__main__":
    merge_dropout_alignments()
    calc_score_merges()
