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
cols = ['am', 'damage_scale', 'vehicle1_moving', 'vehicle2_moving', 
        'pedestrian_involved1', 'pedestrian_involved2', 'cyclist_involved1',
        'cyclist_involved2', 'injury', 'death', 'autonomous_mode', 'conventional_mode',
        'weather', 'lighting', 'road_surface', 'road_condition', 'movement_veh1', 
        'movement_veh2', 'type_of_col_veh1', 'type_of_col_veh2', 'filename']

for col in cols: 
    result[col] = [] 

ct = 0
for file in files: 
    try: 
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
        else: result['pedestrian_involved1'].append(0)

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
        if raw['bicyclist_2'].value: result['cyclist_involved2'].append(1)
        else: result['cyclist_involved2'].append(0)

        # Injury / Death
        if raw['injured'].value or raw['injured_2'].value: result['injury'].append(1)
        else: result['injury'].append(0)
        if raw['deceased'].value or raw['deceased_2'].value: result['death'].append(1)
        else: result['death'].append(0)

        # Autonomous Conventional
        if raw['autonomousmode'].value: result['autonomous_mode'].append(1)
        else: result['autonomous_mode'].append(0)
        if raw['conventionalmode'].value: result['conventional_mode'].append(1)
        else: result['conventional_mode'].append(0)

        # Weather
        try: 
            if raw['weathera1'].value or raw['weathera2'].value: result['weather'].append('clear')
            elif raw['weatherb1'].value or raw['weatherb2'].value: result['weather'].append('cloudy')
            elif raw['weatherc1'].value or raw['weatherc2'].value: result['weather'].append('rain')
            elif raw['weatherd1'].value or raw['weatherd2'].value: result['weather'].append('snow')
            elif raw['weathere1'].value or raw['weathere2'].value: result['weather'].append('fog/vis')
            elif raw['weatherf1'].value or raw['weatherf2'].value: result['weather'].append('other')
            elif raw['weahterg1'].value or raw['weatherg2'].value: result['weather'].append('wind')
            else: result['weather'].append(None)
        except: 
            result['weather'].append(None)

        # Lighting
        try: 
            if raw['lightinga1'].value or raw['lightinga2'].value: result['lighting'].append('daylight')
            elif raw['lightingb1'].value or raw['lightingb2'].value: result['lighting'].append('dusk')
            elif raw['lightingc1'].value or raw['lightingc2'].value: result['lighting'].append('dark-streetlights')
            elif raw['lightingd1'].value or raw['lightingd2'].value or raw['lightinge1'].value or raw['lightinge2'].value: result['lighting'].append('dark-no lights')
            else: result['lighting'].append(None)
        except: 
            result['lighting'].append(None)
        
        # Road Surface
        try: 
            if raw['roadwaya1'].value or raw['roadwaya2'].value: result['road_surface'].append('dry')
            elif raw['roadwayb1'].value or raw['roadwayb2'].value: result['road_surface'].append('wet')
            elif raw['roadwayc1'].value or raw['roadwayc2'].value: result['road_surface'].append('snowy-icy')
            elif raw['roadwayd1'].value or raw['roadwayd2'].value: result['road_surface'].append('slippery')
            else: result['road_surface'].append(None)
        except: 
            result['road_surface'].append(None)

        # Road Condition
        try: 
            if raw['roadconditionsa1'].value or raw['roadconditionsa2'].value: result['road_condition'].append('holes/ruts')
            elif raw['roadconditionsb1'].value or raw['roadconditionsb2'].value: result['road_condition'].append('loose_material')
            elif raw['roadconditionsc1'].value or raw['roadconditionsc2'].value: result['road_condition'].append('obstruction')
            elif raw['roadconditionsd1'].value or raw['roadconditionsd2'].value: result['road_condition'].append('construction_zone')
            elif raw['roadconditionse1'].value or raw['roadconditionse2'].value: result['road_condition'].append('reduced_width')
            elif raw['roadconditionsf1'].value or raw['roadconditionsf2'].value: result['road_condition'].append('flooded')
            elif raw['roadconditionsg1'].value or raw['roadconditionsg2'].value: result['road_condition'].append('other')
            elif raw['roadconditionsh1'].value or raw['roadconditionsh2'].value: result['road_condition'].append('normal')
            else: result['road_condition'].append(None)
        except: 
            result['road_condition'].append(None)

        # Next: movement for both vehicles, type of collision for both vehicles, other factors.
        try:  
            if raw['movementa1'].value: result['movement_veh1'].append('stopped')
            elif raw['movementb1'].value: result['movement_veh1'].append('straight')
            elif raw['movementc1'].value: result['movement_veh1'].append('ran off road')
            elif raw['movementd1'].value: result['movement_veh1'].append('right turn')
            elif raw['movemente1'].value: result['movement_veh1'].append('left turn')
            elif raw['movementf1'].value: result['movement_veh1'].append('u turn')
            elif raw['movementg1'].value: result['movement_veh1'].append('backing')
            elif raw['movementh1'].value: result['movement_veh1'].append('slowing/stopping')
            elif raw['movementi1'].value: result['movement_veh1'].append('passing other veh')
            elif raw['movementj1'].value: result['movement_veh1'].append('changing lanes')
            elif raw['movementk1'].value: result['movement_veh1'].append('parking maneuver')
            elif raw['movementl1'].value: result['movement_veh1'].append('entering traffic')
            elif raw['movementm1'].value: result['movement_veh1'].append('other unsafe turning')
            elif raw['movementn1'].value: result['movement_veh1'].append('xing into opposing lane')
            elif raw['movemento1'].value: result['movement_veh1'].append('parked')
            elif raw['movementp1'].value: result['movement_veh1'].append('merging')
            elif raw['movementq1'].value: result['movement_veh1'].append('traveling wrong way')
            elif raw['movementr1'].value: result['movement_veh1'].append('other')
            else: result['movement_veh1'].append(None)
        except: 
            result['movement_veh1'].append(None)

        try: 
            if raw['movementa2'].value: result['movement_veh2'].append('stopped')
            elif raw['movementb2'].value: result['movement_veh2'].append('straight')
            elif raw['movementc2'].value: result['movement_veh2'].append('ran off road')
            elif raw['movementd2'].value: result['movement_veh2'].append('right turn')
            elif raw['movemente2'].value: result['movement_veh2'].append('left turn')
            elif raw['movementf2'].value: result['movement_veh2'].append('u turn')
            elif raw['movementg2'].value: result['movement_veh2'].append('backing')
            elif raw['movementh2'].value: result['movement_veh2'].append('slowing/stopping')
            elif raw['movementi2'].value: result['movement_veh2'].append('passing other veh')
            elif raw['movementj2'].value: result['movement_veh2'].append('changing lanes')
            elif raw['movementk2'].value: result['movement_veh2'].append('parking maneuver')
            elif raw['movementl2'].value: result['movement_veh2'].append('entering traffic')
            elif raw['movementm2'].value: result['movement_veh2'].append('other unsafe turning')
            elif raw['movementn2'].value: result['movement_veh2'].append('xing into opposing lane')
            elif raw['movemento2'].value: result['movement_veh2'].append('parked')
            elif raw['movementp2'].value: result['movement_veh2'].append('merging')
            elif raw['movementq2'].value: result['movement_veh2'].append('traveling wrong way')
            elif raw['movementr2'].value: result['movement_veh2'].append('other')
            else: result['movement_veh2'].append(None)
        except: 
            result['movement_veh2'].append(None)

        # TYPE OF COLLISION
        try: 
            if raw['typea1'].value: result['type_of_col_veh1'].append('head-on')
            elif raw['typeb1'].value: result['type_of_col_veh1'].append('side-swipe')
            elif raw['typec1'].value: result['type_of_col_veh1'].append('rear end')
            elif raw['typed1'].value: result['type_of_col_veh1'].append('broad-side')
            elif raw['typee1'].value: result['type_of_col_veh1'].append('hit object')
            elif raw['typef1'].value: result['type_of_col_veh1'].append('overturned')
            elif raw['typeg1'].value: result['type_of_col_veh1'].append('veh/pedestrian')
            elif raw['typeh1'].value: result['type_of_col_veh1'].append('other')
            else: result['type_of_col_veh1'].append(None)
        except: 
            result['type_of_col_veh1'].append(None)

        try: 
            if raw['typea2'].value: result['type_of_col_veh2'].append('head-on')
            elif raw['typeb2'].value: result['type_of_col_veh2'].append('side-swipe')
            elif raw['typec2'].value: result['type_of_col_veh2'].append('rear end')
            elif raw['typed2'].value: result['type_of_col_veh2'].append('broad-side')
            elif raw['typee2'].value: result['type_of_col_veh2'].append('hit object')
            elif raw['typef2'].value: result['type_of_col_veh2'].append('overturned')
            elif raw['typeg2'].value: result['type_of_col_veh2'].append('veh/pedestrian')
            elif raw['typeh2'].value: result['type_of_col_veh2'].append('other')
            else: result['type_of_col_veh2'].append(None)
        except: 
            result['type_of_col_veh2'].append(None)

        # Filename
        result['filename'].append(file)
    except: 
        pass

# Save them all to a data frame with the file name in each
final = pd.DataFrame(result)

# Export as pickle --> In the next file, join them together. 
with open('raw_result.pkl', 'wb') as f: 
    pickle.dump(final, f)