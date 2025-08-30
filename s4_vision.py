from pypdf import PdfReader
import os, pdb, sys, pickle
import pandas as pd

path = os.getcwd() + '/dmv_av_collision_reports/'
files = [path + i for i in os.listdir(path)]

def lowercase_dict(original_dict):
    """
    Converts all string keys and string values in a dictionary to lowercase.
    Non-string keys or values remain unchanged.
    """
    new_dict = {}
    for key, value in original_dict.items():
        # Convert key to lowercase if it's a string
        lower_key = key.lower() if isinstance(key, str) else key
        
        # Convert value to lowercase if it's a string
        lower_value = value.lower() if isinstance(value, str) else value
        
        new_dict[lower_key.replace(' ', '')] = lower_value
    return new_dict

result = {} 
cols = ['filename', 'front', 'rear', 'left', 'right']
for col in cols: 
    result[col] = [] 

ct = 0
for file in files: 
    try: 
        print(file)
        val = PdfReader(file)
        raw = lowercase_dict(val.get_fields()) # For checkboxes/radios use raw fields

        left = [i for i in raw.keys() if 'left' in i]
        right = [i for i in raw.keys() if 'right' in i]
        front = [i for i in raw.keys() if 'front' in i]
        rear = [i for i in raw.keys() if 'rear' in i]

        tmpL = [raw[i].value for i in left]
        tmpR = [raw[i].value for i in right]
        tmpF = [raw[i].value for i in front]
        tmpB = [raw[i].value for i in rear]

        tmpL = [i for i in tmpL if str(i).lower() != 'none']
        tmpR = [i for i in tmpR if str(i).lower() != 'none']
        tmpF = [i for i in tmpF if str(i).lower() != 'none']
        tmpB = [i for i in tmpB if str(i).lower() != 'none']

        if len(tmpL) > 0: result['left'].append(1)
        else: result['left'].append(0)
        if len(tmpR) > 0: result['right'].append(1)
        else: result['right'].append(0)
        if len(tmpF) > 0: result['front'].append(1)
        else: result['front'].append(0)
        if len(tmpB) > 0: result['rear'].append(1)
        else: result['rear'].append(0)

    except: 
        result['left'].append(None)
        result['right'].append(None)
        result['front'].append(None)
        result['rear'].append(None)
    result['filename'].append(file)

# Save them all to a data frame with the file name in each

final = pd.DataFrame(result)

df = pd.read_csv('combined_dataset.csv', sep = '~')

df = pd.merge(df, final, how = 'left', on = 'filename')
df.to_csv('combined_dataset_with_vision.csv', sep = '~', index = None)
