from flask import Flask, make_response, jsonify, request, session
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError


from config import app, db
from models import *
from math import log2 , floor

@app.route('/')
def home():
    return 'testing'

@app.route('/testinit')
def test():
    pass

@app.route('/addTournament', methods=['POST'])
def add_Tournament():
    data = request.get_json()

    rounds = floor(log2(len(data['entrants'])))+1

    #create the tournaments and get its id.

    try:
        new_Tournament = Tournament(
            date = data['date'],
            host = data['venue'],
            url = data['url'],
            rounds = rounds
        )
        db.session.add(new_Tournament)
        db.session.commit()
        print(new_Tournament.id)

    except ValueError:
        response = make_response({'Errors':'Failed to Create Tournament'},400)
        return response

    #Create entrants
    new_Entrants = []
    for entrant in data['entrants']:

        user = User.query.filter(User.Konami_id==int(entrant[2])).first()
 
        if user == None:
            user = db.session.query(User).filter(func.similarity(User.name, entrant[1]) > .8).first()
            #Need to handle multiple similarities say we have Nicky Chow and Nocky Chow in users.

        if user:
            #Create Entrant
            try:
                new_Entrant = Entrant(
                    rank = entrant[0],
                    tournament_id = new_Tournament.id, #tournament id from before
                    user_id = user.id
                )
                new_Entrants.append(new_Entrant)
            except ValueError:
                continue #Failed to create entrant should just move to the next one
        else:
            #create user, then create entrant
            print('no user')
            print(entrant)
            try:
                new_user = User(
                    name = entrant[1],
                    Konami_id = entrant[2]
                )
                db.session.add(new_user)
                db.session.commit()
            except SQLAlchemyError as e:
                print(e)
                response = make_response({'Error': 'Failed to create User'},500)
            if new_user:
                try:
                    new_Entrant = Entrant(
                    rank = entrant[0],
                    tournament_id = 1, #tournament id from before
                    user_id = new_user.id
                )
                    new_Entrants.append(new_Entrant)
                except SQLAlchemyError as e:
                    print(e)
                    response = make_response({'Error': 'Failed to create Entrant'},500)
    try:

        db.session.add_all(new_Entrants)
        db.session.commit()

        dict_new_Entrants = [entrant.to_dict() for entrant in new_Entrants]

        response = make_response( jsonify(dict_new_Entrants), 200)
    except SQLAlchemyError as e:
        print(e)
        response = make_response({'Error': 'Failed to commit entrants'},500)

    return response

if __name__ == '__main__':
    app.run(port=5557, debug=True) 