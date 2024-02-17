from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates

from config import db

class Tournament(db.Model, SerializerMixin):
    __tablename__ = 'Tournaments'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String)
    name = db.Column(db.String)
    host = db.Column(db.String)
    url = db.Column(db.String)
    entrants = db.Column(db.Integer)
    rounds = db.Column(db.Integer)

    serialize_rules = ('-Entrant.tournament_info',)
    host_list = ['Gaming Universe',"Gamer's Choice",'Card Quest']
    
    #add Validation for host list

class User(db.Model,SerializerMixin):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    discord_id = db.Column(db.BigInteger)
    konami_id = db.Column(db.String)
    points = db.Column(db.Integer)
    
    #serializer rules
    serialize_rules = ('-Entrant.user_info',)

class Entrant(db.Model,SerializerMixin):
    __tablename__ = 'Entrants'
    id = db.Column(db.Integer, primary_key=True)
    rank = db.Column(db.Integer)

    #foreign_keys
    tournament_id = db.Column(db.Integer, db.ForeignKey('Tournaments.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'))
    
    #Relationships

    tournament_info = db.relationship('Tournament', foreign_keys = [tournament_id], backref = 'Entrant')
    user_info = db.relationship('User', foreign_keys=[user_id], backref = 'Entrant')

    #serializer rules

    serialize_rules = ('-tournament_info.Entrant','-user_info.Entrant')

class Formats(db.Model,SerializerMixin):
    __tablename__ = 'Formats'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
