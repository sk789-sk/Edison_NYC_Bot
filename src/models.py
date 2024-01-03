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
    

class User(db.Model,SerializerMixin):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    discord_id = db.Column(db.BigInteger)
    

class Entrant(db.Model,SerializerMixin):
    __tablename__ = 'Entrants'
    id = db.Column(db.Integer, primary_key=True)
    rank = db.Column(db.Integer)

    #foreign_keys
    tournament = db.Column(db.Integer, db.ForeignKey('Tournaments.id'))
    user = db.Column(db.Integer, db.ForeignKey('Users.id'))