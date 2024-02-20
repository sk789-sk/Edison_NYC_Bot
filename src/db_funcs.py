import math
from models import User
import requests

def calculate_points(t_obj):
    #We need tournament object and the users to update. 
    #Pass in the tournament object which has the entrants and users as well
    #Calculate the number of points for the tournament in total
    #Calculate the points given to each participant
    #Update each Entrant
    #Pass the entrants array back to the db handler
    
    percentage_dict = {
        1: .2500,
        2: .1400,
        3: .1400,
        4: .1400,
        5: .0825,
        6: .0825,
        7: .0825,
        8: .0825
    }

    user_arr = []
    point_total = 0
    entrants = t_obj.Entrant

    sorted_entrants = sorted(entrants, key= lambda x:x.rank)

    for entrant in sorted_entrants:
        user_info = entrant.user_info
        points = math.ceil(user_info.points*.1)
        point_total += points
        user_info.points -= points

    #update points for each user:
    for entrant in sorted_entrants:
        if entrant.rank in percentage_dict:
            earned_points = math.floor(percentage_dict[entrant.rank] * point_total)
            entrant.user_info.points += earned_points
        user_arr.append(entrant.user_info)

    print(point_total)
    print(user_arr)

    return user_arr


if __name__ == '__main__':
    response = requests.get('http://127.0.0.1:5557/allTournamentsTest',timeout=15.0)
    data = response.json()
    test_t = data[0]
    calculate_points(test_t)