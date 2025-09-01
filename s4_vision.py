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
cols = ['filename', 'rear', 'left-back-side', 'left-front-side', 'front', 'right-back-side', 'right-front-side', 'rear-inner-mid', 'front-inner-mid', 'rear-inner-core', 'front-inner-core']
for col in cols: 
    result[col] = [] 

ct = 0
for file in files: 

    print(file)
    val = PdfReader(file)
    raw = lowercase_dict(val.get_fields()) # For checkboxes/radios use raw fields

    try: 
        if raw['leftrear1'].value or raw['rearbumper'].value or raw['rightrear1'].value: result['rear'].append(1)
        else: result['rear'].append(0)
    except: 
        result['rear'].append(0)

    try: 
        if raw['leftrear2'].value or raw['leftrearpassenger1'].value or raw['leftrearpassenger3'].value: result['left-back-side'].append(1)
        else: result['left-back-side'].append(0)
    except: 
        result['left-back-side'].append(0)

    try: 
        if raw['frontdriverside1'].value or raw['frontdriverside3'].value or raw['leftfrontcorner1'].value: result['left-front-side'].append(1)
        else: result['left-front-side'].append(0)
    except: 
        result['left-front-side'].append(0)

    try: 
        if raw['leftfrontcorner3'].value or raw['frontbumper'].value or raw['rightfrontcorner3'].value: result['front'].append(1)
        else: result['front'].append(0)
    except: 
        result['front'].append(0)

    try: 
        if raw['rightrear3'].value or raw['rightrearpassenger2'].value or raw['rightrearpassenger4'].value: result['right-back-side'].append(1)
        else: result['right-back-side'].append(0)
    except: 
        result['right-back-side'].append(0)

    try: 
        if raw['frontpassengerside2'].value or raw['frontpassengerside4'].value or raw['rightfrontcorner2'].value: result['right-front-side'].append(1)
        else: result['right-front-side'].append(0)
    except: 
        result['right-front-side'].append(0)

    try: 
        if raw['leftrear3'].value or raw['rightrear2'].value: result['rear-inner-mid'].append(1)
        else: result['rear-inner-mid'].append(0)
    except: 
        result['rear-inner-mid'].append(0)

    try: 
        if raw['leftfrontcorner2'].value or raw['rightfrontcorner1'].value: result['front-inner-mid'].append(1)
        else: result['front-inner-mid'].append(0)
    except: 
        result['front-inner-mid'].append(0)

    try: 
        if raw['leftrearpassenger2'].value or raw['leftrearpassenger4'].value or raw['rightrearpassenger1'].value or raw['rightrearpassenger3'].value: result['rear-inner-core'].append(1)
        else: result['rear-inner-core'].append(0)
    except: 
        result['rear-inner-core'].append(0)

    try: 
        if raw['frontdriverside2'].value or raw['frontdriverside4'].value or raw['frontpassengerside1'].value or raw['frontpassengerside3'].value: result['front-inner-core'].append(1)
        else: result['front-inner-core'].append(0)
    except: 
        result['front-inner-core'].append(0)

    result['filename'].append(file)

# Save them all to a data frame with the file name in each

final = pd.DataFrame(result)

df = pd.read_csv('combined_dataset.csv', sep = '~')

df = pd.merge(df, final, how = 'left', on = 'filename')
df.to_csv('combined_dataset_with_vision.csv', sep = '~', index = None)




"""
Car Box Mapping Key
Left Rear 1	1_REAR	
Left Front Corner 3	10_FRONT	
Front Bumper	11_FRONT	
Right Front Corner 3	12_FRONT	
Right Rear 3	13_RREAR	
Right Rear Passenger 2	14_RREAR	
Right Rear Passenger 4	15_RREAR	
Front Passenger Side 2	16_RFRONT	
Front Passenger Side 4	17_RFRONT	
Right Front Corner 2	18_RFRONT	
Left Rear 3	19_INREAR	
Rear Bumper	2_REAR	
Right Rear 2	20_INREAR	
Left Front Corner 2	21_INFRONT	
Right Front Corner 1	22_INFRONT	
Left Rear Passenger 2	23_RPASSENGER	
Left Rear Passenger 4	24_RPASSENGER	
Right Rear Passenger 1	25_RPASSENGER	
Right Rear Passenger 3	26_RPASSENGER	
Front Driver Side 2	27_FPASSENGER	
Front Driver Side 4	28_FPASSENGER	
Front Passenger Side 1	29_FPASSENGER	
Right Rear 1	3_REAR	
Front Passenger Side 3	30_FPASSENGER	
Left Rear 2	4_LREAR	
Left Rear Passenger 1	5_LREAR	
Left Rear Passenger 3	6_LREAR	
Front Driver Side 1	7_LFRONT	
Front Driver Side 3	8_LFRONT	
Left Front Corner 1	9_LFRONT	
"""