from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates, Mapped , mapped_column , relationship
from sqlalchemy import String , Integer, DateTime , BigInteger, Boolean , ARRAY , Float
from sqlalchemy.ext.mutable import MutableList



from typing import Optional


from config import db

class OnlineTournament(db.Model, SerializerMixin):
    __tablename__ = 'online_tournaments'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    game: Mapped[str] = mapped_column(String(25))
    format: Mapped[str] = mapped_column(String(25))
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=db.func.now()
    )
    status: Mapped[str] = mapped_column(String(25))
    current_round: Mapped[int] = mapped_column(Integer)
    total_rounds: Mapped[int]
    creator_id: Mapped[int] = mapped_column(BigInteger)
    guild_id: Mapped[int] = mapped_column(BigInteger)
    is_paid: Mapped[bool] = mapped_column(Boolean)
    
    # id = db.Column(db.Integer, primary_key=True)
    # name = db.Column(db.String)
    # game = db.Column(db.String)
    # format = db.Column(db.String)
    # created_at = db.Column(db.DateTime(timezone=True), default=db.func.now()) #may modify
    # status = db.Column(db.String)
    # current_round = db.Column(db.Integer, default = 0)
    # total_rounds = db.Column(db.Integer)
    # creator_id = db.Column(db.BigInteger)
    # guild_id = db.Column(db.BigInteger)
    # is_paid = db.Column(db.Boolean)

    #FKs
    #Relationships
    #Validations

    @validates('format')
    def validate_format(self,key,format):
        if format in ['Swiss','Double Elimination','Single Elimination','Round Robin']:
            return format
        raise ValueError

    def __repr__(self):
        return f"<Tournament_id={self.id} Tournament_name={self.name}>"

class OnlineMatch(db.Model,SerializerMixin):
    __tablename__ = 'online_match'
    id: Mapped[int] = mapped_column(primary_key=True)
    # result: Mapped[int]
    winners_id: Mapped[Optional[int]]
    losers_id: Mapped[Optional[int]]
    is_tie: Mapped[Optional[bool]] #Only relevant in swiss 
    round: Mapped[Optional[int]] #not all matches have a round only relevant for swiss imo

    #FKs
    tournament_id: Mapped[int] = mapped_column(db.ForeignKey("online_tournaments.id"))
    player_1_id: Mapped[int] = mapped_column(db.ForeignKey("online_tournament_entrants.id"))
    player_2_id: Mapped[int] = mapped_column(db.ForeignKey("online_tournament_entrants.id"))

    winners_next_match:Mapped[int] = mapped_column(db.ForeignKey("online_match.id"))
    losers_next_match:Mapped[int] = mapped_column(db.ForeignKey("online_match.id"))

    #relationships
    #Winners Next Match (actual Match)
    #Losers Next Match (actual Match)

    def __repr__(self):
        return f"<Match between player_1 {self.player_1_id} and player_2 {self.player_2_id} in tournament_id {self.tournament_id}>"
class OnlineTournamntEntrant(db.Model,SerializerMixin):
    __tablename__ = 'online_tournament_entrants'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50))
    discord_id: Mapped[int] = mapped_column(BigInteger)
    point_total: Mapped[int] = mapped_column(Integer)
    opponents: Mapped[list[int]] = mapped_column(MutableList.as_mutable(ARRAY(Integer)))
    dropped: Mapped[bool] = mapped_column(Boolean)
    pair_up_down: Mapped[bool] = mapped_column(Boolean)
    bye: Mapped[bool] = mapped_column(Boolean)
    SOS: Mapped[float] = mapped_column(Float)
    SOSOS: Mapped[float] = mapped_column(Float)
    Bucholz: Mapped[int] = mapped_column(Integer)
    medianBucholz: Mapped[int] = mapped_column(Integer)
    bucholzCut1: Mapped[int] = mapped_column(Integer)

    #FK
    tournament_id: Mapped[int] = mapped_column(db.ForeignKey("tournaments.id"), nullable=False)


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

class User(db.Model,SerializerMixin):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    discord_id = db.Column(db.BigInteger)
    konami_id = db.Column(db.BigInteger)
    join_date = db.Column(db.Integer)
    

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