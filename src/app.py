from flask import Flask, make_response, jsonify, request, session
from sqlalchemy import func , desc
from sqlalchemy.exc import SQLAlchemyError 
from sqlalchemy.orm import joinedload


from config import app, db
from models import *
from math import log2 , floor

alias_mapping = {
        'gu' : 'Gaming  Universe',
        'gaminguniverse' : 'Gaming Universe',
        'gc' : "Gamer's Choice",
        "gamerschoice" : "Gamer's Choice",
        "gamer'schoice" : "Gamer's Choice",
        'cq' : 'Card Quest',
        "cardquest" : 'Card Quest'
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
    processedVenue = data['venue'].lower().replace(" ","")

    try:
        new_Tournament = Tournament(
            date = data['date'],
            host = alias_mapping.get(processedVenue),
            url = data['url'],
            rounds = rounds
        )
        db.session.add(new_Tournament)
        db.session.flush()

        #db.session.commit()
        print(new_Tournament.id)

    except ValueError:
        response = make_response({'Errors':'Failed to Create Tournament, validation error'},400)
        return response

    #Create entrants
    new_Entrants = []
    new_users = []
    failed_entrants = []
    for entrant in data['entrants']:

        user = User.query.filter(User.konami_id==int(entrant[2])).first()
 
        if user == None:

            potential_users = db.session.query(User).filter(func.levenshtein(User.name, entrant[1]) < 5).order_by(func.levenshtein(User.name, entrant[1])).all()

            if len(potential_users) !=0:
                user = potential_users[0]
        
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
                failed_entrants.append(user)
                continue #Failed to create entrant for user. 
        else:
            #create user, then create entrant
            print(f'no user for {entrant}')
            try:
                new_user = User(
                    name = entrant[1],
                    konami_id = entrant[2]
                )

                new_users.append(new_user)
                db.session.add(new_user)
                db.session.flush()
                #db.session.commit()

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
    print(f'Failed to create entrants fof {failed_entrants}')
    print(f'Created new Users for {new_users}')

    return response

@app.route('/userResults', methods = ['GET'])
def getUserResults():
    # params = request.args.to_dict()

    #We get back either a discord id or a konami id. 
    #We then create a filter for that

    filter_functions = {
        'name' : lambda value: User.name.ilike(f'%{value}%'),
        'discord_id' : lambda value: User.discord_id == value,
        'konami_id' : lambda value: User.konami_id == value

    }

    filters = []

    for key, value in request.args.items():
        if key in filter_functions:
            filter_element = filter_functions[key](value)
            filters.append(filter_element)
        else:
            print('Filter param unsupported')    

    # for key in request.args:
    #     print(key,request.args[key])

    #     filter_element = getattr(User,key)==request.args[key]
    #     filters.append(filter_element)
    
    users = User.query.filter(*filters).all()

    #convert htis to all() check for length [0,1,1+]

    print(users)

    #sort and turn into dict is better
    for user in users:
        user.Entrant = sorted(user.Entrant, key= lambda x: x.tournament_info.date, reverse=True)
    
    # if len(users)==1:
    #     data = [user.to_dict() for user in users]
    #     response = make_response(jsonify(data),200)

    #     # user = users[0]        
    #     # user.Entrant = sorted(user.Entrant, key= lambda x: x.tournament_info.date, reverse=True)
    #     # response = make_response(jsonify(user.to_dict()),200)
    if len(users) == 0:
        response = make_response({},404)
    else:
        #We have multiple users. Shuld handle this in the bot front instead of here
        data = [user.to_dict() for user in users]
        response = make_response(jsonify(data),200)
    return response

@app.route('/allTournamentsTest')
def returnAllTournaments():

    limit = None

    if request.args.get('limit') is not None:
        limit = int(request.args.get('limit'))

    tournament_list = Tournament.query.order_by(Tournament.date.desc()).limit(limit).all()
    r = [tournament.to_dict() for tournament in tournament_list]

    response = make_response(jsonify(r),200)
    return response

@app.route('/tournamentResults')
def getTournamentResults():
    #There are 2 options happening. First we give you the database_id and can identify from that
    #The second option is pass in an filter arguements, date and venue and use that to get the tournament corresponding with it, 

    limit = None

    if request.args.get('limit') is not None:
        limit = int(request.args.get('limit'))


    filters = []
    for key in request.args:

        if key == 'limit':
            continue
        else:
            print(key,request.args[key])
            filter_element = getattr(Tournament,key)==request.args[key]
            filters.append(filter_element)
        
    # t_list = Tournament.query.filter(*filters).all()

    t_list = Tournament.query.filter(*filters).order_by(Tournament.date.desc()).limit(limit).all()
    if len(t_list)>0:
        t_dict = [t.to_dict() for t in t_list]
        response = make_response(jsonify(t_dict),200)
    else:
        response = make_response({},404)
    return response

@app.route('/tournamentresultsid/<int:id>')
def getTournamentResultsbyid(id):

    tournament = Tournament.query.filter(Tournament.id ==id).first_or_404()
    response = make_response(jsonify(tournament.to_dict()),200)
    return response

@app.route('/Register', methods=['POST'])
def register():
    pass

if __name__ == '__main__':
    app.run(port=5557, debug=True) 