import pandas as pd
import numpy as np
import os, pdb, sys, pickle

with open('raw_result.pkl', 'rb') as f:
    raw_result = pickle.load(f)

with open('files_output.pkl', 'rb') as f:
    files_output = pickle.load(f)

df = pd.merge(files_output, raw_result, how = 'left', on = 'filename')

## FORMATTING

# Remove any null columns
drops = [] 
for col in df.columns: 
    df[col] = [i if str(i) != '' else None for i in df[col]]
    if df[col].isnull().all(): 
        drops.append(col)

# Renames: 0.6: accident_location, 0.7: accident_city, 1.6: crash_zip, 1.7: addtl_desc, 1.8: desc, 
df['accident_loc'] = df['0.6']
df = df.drop(columns = ['0.6'])

df['accident_city'] = df['0.7']
df = df.drop(columns = ['0.7'])

df['accident_zip'] = df['1.6']
df = df.drop(columns = ['1.6'])

df['addtl_desc'] = df['1.7']
df = df.drop(columns = ['1.7'])

df['desc'] = df['1.8']
df = df.drop(columns = ['1.8'])

drops = drops + ['0.6', '0.7', '1.6', '1.7', '1.8']
df = df.drop(columns = [i for i in df.columns if i[0] in ['0', '1']])

df['desc'] = [str(df['desc'][i]) + ' ' + str(df['addtl_desc'][i]) for i in range(len(df))]
df = df.drop(columns = ['addtl_desc'])
df['desc'] = [i[:-4] if i[-4:] == 'None' else i for i in df['desc']]

df.to_csv('combined_dataset.csv', index = None, sep = "~")