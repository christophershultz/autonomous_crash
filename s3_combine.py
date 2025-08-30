import pandas as pd
import numpy as np
import os, pdb, sys, pickle

with open('raw_result.pkl', 'rb') as f:
    raw_result = pickle.load(f)

with open('files_output.pkl', 'rb') as f:
    files_output = pickle.load(f)

pdb.set_trace()
df = pd.merge(files_output, raw_result, how = 'left', on = 'filename')
df.to_csv('combined_dataset.csv', index = None, sep = "~")