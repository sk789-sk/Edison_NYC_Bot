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
    rounds = db.Column(db.Integer)

    serialize_rules = ('-Entrant.tournament_info',)

    host_list = ['Gaming Universe',"Gamer's Choice",'Card Quest','Collectors Emporium']
    
    #add Validation for host list
    @validates('host')
    def validate_host(self,key,host):
        if host not in self.host_list:
            raise ValueError(f"Invalid host")
        return host

class User(db.Model,SerializerMixin):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    discord_id = db.Column(db.BigInteger)
    konami_id = db.Column(db.BigInteger)

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