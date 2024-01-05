from flask import Flask, make_response, jsonify, request, session
from sqlalchemy import func , desc
from sqlalchemy.exc import SQLAlchemyError 


from config import app, db
from models import *
from math import log2 , floor

alias_mapping = {
        'gu' : 'Gaming  Universe',
        'gaming universe' : 'Gaming Universe',
        'gc' : "Gamer's Choice",
        "gamers choice" : "Gamer's Choice",
        'cq' : 'Card Quest',
        "card quest" : 'Card Quest'
}


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

    #Aliases for venues
    
    #lowercase the entry and remove the whitespaces

    input = data['venue']

    processedVenue = input.lower().replace(" ","")



    alias_mapping = {
        'gu' : 'Gaming  Universe',
        'gaminguniverse' : 'Gaming Universe',
        'gc' : "Gamer's Choice",
        "gamerschoice" : "Gamer's Choice",
        'cq' : 'Card Quest',
        "cardquest" : 'Card Quest'
    }



    try:
        new_Tournament = Tournament(
            date = data['date'],
            host = alias_mapping.get(processedVenue),
            url = data['url'],
            rounds = rounds
        )
        db.session.add(new_Tournament)
        db.session.commit()
        print(new_Tournament.id)

    except ValueError:
        response = make_response({'Errors':'Failed to Create Tournament, validation error'},400)
        return response

    #Create entrants
    new_Entrants = []
    for entrant in data['entrants']:

        user = User.query.filter(User.konami_id==int(entrant[2])).first()
 
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
                    konami_id = entrant[2]
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
                    tournament_id = new_Tournament.id, #tournament id from before
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

@app.route('/userResults', methods = ['GET'])
def getUserResults():
    # params = request.args.to_dict()

    #We get back either a discord id or a konami id. 
    #We then create a filter for that
    filters = []
    for key in request.args:
        print(key,request.args[key])

        filter_element = getattr(User,key)==request.args[key]
        filters.append(filter_element)
    
    user = User.query.filter(*filters).first()

    # user = User.query.filter(User.discord_id==discord_id).first()
    if user:
        print(user)
        response = make_response(jsonify(user.to_dict()),200)
    else:
        response = make_response({},404)    
    return response

@app.route('/allTournaments')
def returnAllTournaments():

    limit = None

    if request.args.get('limit') is not None:
        limit = int(request.args.get('limit'))


    tournament_list = Tournament.query.order_by(Tournament.date.desc()).limit(limit).all()

    print(Tournament.query.order_by(Tournament.date.desc()).limit(10).statement)
    print(Tournament.query.order_by(Tournament.date.desc()).limit(None).statement)

    r = [tournament.to_dict() for tournament in tournament_list]

    response = make_response(jsonify(r),200)
    return response

@app.route('/tournamentResults')
def getTournamentResults():
    #There are 2 options happening. First we give you the database_id and can identify from that
    #The second option is i pass in an filter arguements, date and venue and use that to get the tournament corresponding with it, 
    pass

@app.route('/Register', methods=['POST'])
def register():
    pass

if __name__ == '__main__':
    app.run(port=5557, debug=True) 