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
        
        new_dict[lower_key] = lower_value
    return new_dict

result = None

ct = 0
for file in files: 
    try: 
        print(file)
        val = PdfReader(file)
        fields = lowercase_dict(val.get_form_text_fields()) # text/combos
        
        if result is None: 
            result = fields.copy()
            result['filename'] = file

            for key in result.keys(): 
                result[key] = [result[key]]
        else: 
            fields['filename'] = file
            for key in result.keys(): 
                result[key].append(fields[key] if key in fields else None)
    except: 
        pass

res = pd.DataFrame(result)

with open('files_output.csv', 'wb') as f: 
    pickle.dump(res, f)

print("DONE")