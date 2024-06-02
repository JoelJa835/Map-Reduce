import numpy as np
from numpy import random
import requests

def randomData_jason():
    ''' Return a JASON file with random 
    '''
    days=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    value_row = np.random.randint(10, size=7)
    print(value_row)
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

def updateDays_sum():
    for key,val in data_json.items():
        dic_cum[key] += val


days=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]



data_json = randomData_jason()
print(data_json)
updateDays_sum()
print(dic_cum,'\n\n')

data_json = randomData_jason()
print(data_json)
updateDays_sum()
print(dic_cum,'\n\n')
# Serializing json
#json_object = json.dumps(dictionary, indent=3)
 
# Writing to sample.json
#with open("sample.json", "w") as outfile:
#    outfile.write(json_object)


#with open('sample.json') as f:
#    d = json.load(f)

