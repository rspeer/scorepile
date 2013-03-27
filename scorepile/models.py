from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import (Column, String, Integer, Boolean, DateTime,
                        ForeignKey, desc)
import json

Base = declarative_base()


class DataMixin:
    """
    A mixin for storing extra JSON data on each row. SQL won't care about
    the contents of this data.
    """
    jsondata = Column(String, default='{}')
    
    def _get_data(self):
        return json.loads(self.jsondata)

    def _set_data(self, value):
        self.jsondata = json.dumps(value)

    data = property(_get_data, _set_data)


class Player(Base, DataMixin):
    """
    A registered player on Iso, whom we can track across multiple games.

    We don't track unregistered players.
    """
    __tablename__ = 'players'
    id = Column(Integer, primary_key=True)

    # iso_id: the 27-character persistent ID that is assigned to each player
    # in the game logs. If a player changes their name, we'll know it's the
    # same player because of the iso_id.
    iso_id = Column(String(27), index=True, unique=True, nullable=True)

    # The player's current displayed name.
    name = Column(String, index=True)

    # A one-to-many list of games the player has played, by way of GamePlayer
    # objects.
    games = relationship('GamePlayer', order_by='desc(GamePlayer.id)',
                         backref='player')


class GamePlayer(Base, DataMixin):
    """
    A player in a particular game.

    We store a reference to the 'players' table if the player is registered,
    but we also store the player's name for this game. This allows at least
    referring to unregistered users by their name, and keeps the log consistent
    when a player has changed their name.
    """
    __tablename__ = 'game_players'
    id = Column(Integer, primary_key=True)

    # player_index: the identifier such as 'p0' or 'p1' that distinguishes the
    # player through most of the game log. I'm not sure that it actually has
    # anything to do with who took the first turn.
    player_index = Column(String)

    # Link to the game, and to the player if the player is registered.
    game_id = Column(Integer, ForeignKey('games.id'), index=True)
    player_id = Column(Integer, ForeignKey('players.id'), index=True,
                       nullable=True)
    
    # The player's current name.
    player_name = Column(String)
    
    # Did this player win this game?
    winner = Column(Boolean)

class Game(Base, DataMixin):
    __tablename__ = 'games'
    id = Column(Integer, primary_key=True)

    # How many players were in the game?
    nplayers = Column(Integer)

    # What's the relative URL of the game log?
    url = Column(String)

    # When was the game played?
    timestamp = Column(DateTime, index=True)
    
    # How did the game end?
    win_condition = Column(String)

    # A one-to-many list of players in the game and information about them,
    # using GamePlayer objects.
    players = relationship('GamePlayer', order_by='player_index',
                           backref='game')

