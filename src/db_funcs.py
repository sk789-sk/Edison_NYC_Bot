import math
from models import User
import requests

response = requests.get('http://127.0.0.1:5557/allTournamentsTest')
data = response.json()
test_t = data[0]

def calculate_standings(t_obj):
    #We need tournament object and the users to update. 
    #Pass in the tournament object which has the entrants and users as well

    user_arr = []


    point_total = 0
    entrants = t_obj['Entrant']

    for entrant in entrants:
        user_info = entrant['user_info']
        points = math.ceil(user_info['points']*.1)
        point_total += points
        user_info['points'] -= points
        #Create a User Obj for the database
        user_arr.append(user_info)

    print('hihi')
    pass

print(test_t)