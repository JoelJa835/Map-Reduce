import numpy as np
from numpy import random
import requests

def randomData_json():
    ''' Return a JASON file with random value for each day
    '''
    days=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    value_row = np.random.randint(10, size=7)
    return {i:v for i,v in zip(days, value_row)} #(days_row, value_row)


dic_cum={
    "Monday": 0.0,
    "Tuesday": 0.0,
    "Wednesday":0.0,
    "Thursday":0.0,
    "Friday":0.0,
    "Saturday":0.0,
    "Sunday": 0.0,
    }
""" A dictionary holds a cumulative sum for each day"""

dic_list={
    "Monday": [],
    "Tuesday": [],
    "Wednesday":[],
    "Thursday":[],
    "Friday":[],
    "Saturday":[],
    "Sunday": [],
    }
""" A dictionary holds a list of valu for each day"""

def update_Days_sum():
    """ Adds the value form the data_json to dic_cum dictionary """
    for key,val in data_json.items():
        dic_cum[key] += val

def update_Days_list():
    """ Appends the value form the data_json to dic_list dictionary """
    for key,val in data_json.items():
        dic_list[key].append(val)

days=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


#create a random json 
data_json = randomData_json()
#Adds the value form the data_json to dic_cum dictionary
update_Days_sum()
# Appends the value form the data_json to dic_list dictionary
update_Days_list()

print("dic_cum",':',dic_cum)
print("dic_list",':',dic_list)



# Serializing json
#json_object = json.dumps(dictionary, indent=3)
 
# Writing to sample.json
#with open("sample.json", "w") as outfile:
#    outfile.write(json_object)


#with open('sample.json') as f:
#    d = json.load(f)

