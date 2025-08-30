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

result = {'am': []}


ct = 0
for file in files: 
    print(file)
    val = PdfReader(file)
    raw = lowercase_dict(val.get_fields()) # For checkboxes/radios use raw fields

    # AM/PM
    if raw['am'].value: result['am'].append(1)
    else: result['am'].append(0)

    # Vehicle Moving
    if raw['moving'].value: result['vehicle1_moving'].append(1)
    else: result['vehicle1_moving'].append(0)

    # Pedestrian Involved
    if raw['pedestrian'].value: result['pedestrian_involved1'].append(1)
    else: result['pedestrian_involved'].append(0)

    # Cyclist Involved
    if raw['bicyclist'].value: result['cyclist_involved1'].append(1)
    else: result['cyclist_involved1'].append(0)

    # Damage Scale
    if raw['major'].value: result['damage_scale'].append(4)
    elif raw['moderate'].value: result['damage_scale'].append(3)
    elif raw['minor'].value: result['damage_scale'].append(2)
    elif raw['none'].value: result['damage_scale'].append(1)
    else: result['damage_scale'].append(None)
    
    # Vehicle Moving
    if raw['moving_2'].value: result['vehicle2_moving'].append(1)
    else: result['vehicle2_moving'].append(0)

    # Pedestrian Involved
    if raw['pedestrian_2'].value: result['pedestrian_involved2'].append(1)
    else: result['pedestrian_involved2'].append(0)

    # Cyclist Involved
    if raw['bicyclist_2'].value: result['cyclist_involved1'].append(1)
    else: result['cyclist_involved1'].append(0)

    # Injury / Death
    if raw['injury'].value or raw['injury_2'].value: result['injury'].append(1)
    else: result['injury'].append(0)
    if raw['deceased'].value or raw['deceased_2'].value: result['death'].append(1)
    else: result['death'].append(0)

    # Autonomous Conventional
    if raw['autonomous'].value: result['autonomous_mode'].append(1)
    else: result['autonomous'].append(0)
    if raw['conventional mode'].value: result['conventional_mode'].append(1)
    else: result['conventional_mode'].append(0)

    # Weather
    if raw['weather a 1'].value or raw['weather a 2'].value: result['weather'].append('clear')
    elif raw['weather b 1'].value or raw['weather b 2'].value: result['weahter'].append('cloudy')
    elif raw['weather c 1'].value or raw['weather c 2'].value: result['weather'].append('rain')
    elif raw['weather d 1'].value or raw['weather d 2'].value: result['weather'].append('snow')
    elif raw['weather e 1'].value or raw['weather e 2'].value: result['weather'].append('fog/vis')
    elif raw['weather f 1'].value or raw['weather f 2'].value: result['weather'].append('other')
    elif raw['weahter g 1'].value or raw['weather g 2'].value: result['weather'].append('wind')
    else: result['weather'].append(None)

    # Lighting
    if raw['lighting a 1'].value or raw['lighting a 2'].value: result['lighting'].append('daylight')
    elif raw['lighting b 1'].value or raw['lighting b 2'].value: result['lighting'].append('dusk')
    elif raw['lighting c 1'].value or raw['lighting c 2'].value: result['lighting'].append('dark-streetlights')
    elif raw['lighting d 1'].value or raw['lighting d 2'].value or raw['lighting e 1'].value or raw['lighting e 2'].value: result['lighting'].append('dark-no lights')
    else: result['lighting'].append(None)
    break

pdb.set_trace()