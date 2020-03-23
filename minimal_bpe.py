# minimal BPE from arxiv 1508.07909
# to apply at test time

import re
import collections

def get_stats(vocab):
  '''
  Input: dictionary with words as keys, splitted, and an end of word character </w>
    ex: 'l o w e r </w>'
    and frequency of word as value
  Output: dictionary with tuple of characters as key,
    and frequency of tuple/bigram as value.
  '''
  pairs = collections.defaultdict(int)
  for word, freq in vocab.items():
    symbols = word.split()
    for i in range(len(symbols)-1):
      pairs[symbols[i], symbols[i+1]] += freq
  return pairs

def merge_vocab(pair, v_in):
  v_out = {}
  # escape space
  bigram = re.escape(' '.join(pair))
  p = re.compile(r'(?<!\S)' + bigram + r'(?!\S)') # don't understand the regex. but it merges the bigram chars together
  for word in v_in:
    w_out = p.sub(''.join(pair), word)
    v_out[w_out] = v_in[word]
  return v_out


vocab = {'l o w </w>': 5,
         'l o w e r </w>': 2,
         'n e w e s t </w>': 6,
         'w i d e s t </w>': 3}
num_merges = 15
for i in range(num_merges):
  pairs = get_stats(vocab)
  try:
    best = max(pairs, key=pairs.get)
  except ValueError:
    break
  if pairs[best] < 2:
     sys.stderr.write('no pair has frequency > 1. Stopping\n')
     break
  vocab = merge_vocab(best, vocab)
  print(best)
