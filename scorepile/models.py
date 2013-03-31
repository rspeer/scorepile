from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, joinedload
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import (Column, String, Integer, Boolean, DateTime,
                        ForeignKey, desc)
import json
import logging
from . import dateutils
from jinja2 import Template

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)
Base = declarative_base()


class DataMixin:
    """
    A mixin for storing extra JSON data on each row. SQL won't care about
    the contents of this data.

    This requires defining a 'jsondata' column. We could define it here and
    inherit it, but that would constitute using OOP to add confusion.
    """
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
    
    jsondata = Column(String, default='{}')

    @property
    def iso_id_url(self):
        return self.iso_id.replace('+', '-').replace('/', '_')
        
    @staticmethod
    def from_parse_data(parsed):
        return Player(
            name=parsed['name'],
            iso_id=parsed['iso_id']
        )

    @staticmethod
    def get_by_iso_id(session, iso_id):
        if iso_id is None:
            return None
        iso_id = iso_id.replace('-', '+').replace('_', '/')

        try:
            found = session.query(Player).filter(Player.iso_id == iso_id).one()
            return found
        except NoResultFound:
            return None

    @staticmethod
    def get_by_name(session, name):
        try:
            found = session.query(Player).filter(Player.name == name).one()
            return found
        except NoResultFound:
            return None

    def played_games(self, session, day=None, limit=1000):
        played = (session.query(GamePlayer)
                         .join(GamePlayer.game)
                         .filter(GamePlayer.player == self)
                         .filter(Game.nplayers >= 2)
                         .order_by(desc(Game.timestamp)))
        if day is not None:
            day_start = dateutils.midnight_before(day)
            day_end = dateutils.midnight_after(day)
            played = (played.filter(Game.timestamp >= day_start)
                            .filter(Game.timestamp < day_end))
        played = played.limit(limit)
        return [item.game for item in played]
    
    def __repr__(self):
        return '<Player: {0}>'.format(self.name, self.iso_id)

    def html(self):
        template = Template(
            '<a href="/player/id/{{ player.iso_id_url }}" class="player">'
            '{{ player.name }}'
            '</a>'
        )
        return template.render(player=self)


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
    
    jsondata = Column(String, default='{}')

    @staticmethod
    def from_parse_data(parsed, player_index, player_obj):
        info = parsed['players'][player_index]
        gp = GamePlayer(
            #game_id=parsed['game_id'],
            player_index=player_index,
            winner=info['winner'],
            player_name=info['name']
        )
        gp.data = info['data']
        if player_obj is not None:
            gp.player = player_obj
        return gp

    def __repr__(self):
        return '<GamePlayer: {} in game #{})>'.format(self.player_name, self.game_id)

    def html(self):
        "Render this player's name, including a possible link, as HTML."
        if self.player_id:
            template = Template(
                '<a href="/player/id/{{ gplayer.player.iso_id_url }}" class="reg player">'
                '{{ gplayer.player_name }}'
                '</a>'
            )
        else:
            template = Template(
                '<span class="unreg player">{{ gplayer.player_name }}</span>'
            )
        return template.render(gplayer=self)


class Game(Base, DataMixin):
    __tablename__ = 'games'
    id = Column(Integer, primary_key=True)

    # How many players were in the game?
    nplayers = Column(Integer)

    # Did it use the expansion?
    cardset = Column(String)

    # What's the relative URL of the game log?
    url = Column(String)

    # When was the game played?
    timestamp = Column(DateTime, index=True)
    
    # A one-to-many list of players in the game and information about them,
    # using GamePlayer objects.
    players = relationship('GamePlayer',
                           order_by=(desc(GamePlayer.winner),
                                     GamePlayer.player_index),
                           backref='game', cascade='all, delete-orphan')

    jsondata = Column(String, default='{}')

    def friendly_timestamp(self):
        datestr = dateutils.friendly_date(self.timestamp)
        timestr = dateutils.friendly_time(self.timestamp)
        return datestr + ', ' + timestr
    
    @staticmethod
    def get(session, id):
        try:
            found = session.query(Game).filter(Game.id == id).one()
            return found
        except NoResultFound:
            return None

    @staticmethod
    def games_on_day(session, timestamp):
        day_start = dateutils.midnight_before(timestamp)
        day_end = dateutils.midnight_after(timestamp)
        results = (session.query(Game)
                          .options(joinedload(Game.players))
                          .filter(Game.timestamp >= day_start)
                          .filter(Game.timestamp < day_end)
                          .filter(Game.nplayers >= 2)
                          .order_by(Game.id))
        return results

    @staticmethod
    def from_parse_data(parsed):
        game = Game(
            id=parsed['game_id'],
            nplayers=parsed['nplayers'],
            url=parsed['url'],
            timestamp=parsed['timestamp'],
            cardset=parsed['cardset']
        )
        game.data = {'win_condition': parsed['win_condition']}
        return game

    @staticmethod
    def create(session, parsed, commit=True):
        existing = Game.get(session, parsed['game_id'])
        if existing:
            game = existing
            LOG.warn('Found existing {}'.format(game))
        else:
            game = Game.from_parse_data(parsed)

        players = []
        for idx, playerdata in parsed['players'].items():
            if playerdata['iso_id']:
                player = Player.get_by_iso_id(session, playerdata['iso_id'])
                if player is None:
                    player = Player.from_parse_data(playerdata)
                else:
                    player.name = playerdata['name']
                session.add(player)
            else:
                player = None

            gp = GamePlayer.from_parse_data(parsed, idx, player)
            players.append(gp)
        
        game.players = players
        session.add(game)
        LOG.info("Added {}".format(game))

        if commit:
            session.commit()

    def winners(self):
        return [player for player in self.players if player.winner == True]
    
    def losers(self):
        return [player for player in self.players if player.winner == False]

    def icon_name(self):
        """
        Associate a thematic icon with each win condition.
        """
        cond = self.data['win_condition']
        if cond == 'attrition':
            return 'castle'
        elif cond == 'achievements':
            return 'crown'
        elif cond == 'score':
            return 'leaf'
        else:
            return 'clock'

    def grid_width(self):
        return max(3, 12 // self.nplayers)

    def __repr__(self):
        players = self.players
        if players:
            return '<Game #{}: {}>'.format(self.id, players)
        else:
            return '<Game #{}>'.format(self.id)

    def html(self):
        "Give this game an HTML-formatted title for use in templates."
        winnerdesc = ', '.join(p.html() for p in self.winners())
        loserdesc = ', '.join(p.html() for p in self.losers())
        if len(self.losers()) == 0:
            playerdesc = ' = '.join(p.html() for p in self.players)
        else:
            playerdesc = '{} &gt; {}'.format(winnerdesc, loserdesc)

        template = Template(
            '<a href="{{ game.url }}" class="gameid">#{{ game.id }}</a>: '
            '{{ playerdesc|safe }} by '
            '<span class="condition">{{ game.data.win_condition }}</span>'
        )
        return template.render(game=self, playerdesc=playerdesc)


def create_tables():
    from scorepile.db import ENGINE
    Base.metadata.create_all(ENGINE)


def delete_tables():
    from scorepile.db import ENGINE
    Base.metadata.drop_all(ENGINE)


# This file can be run as a script from the command line.
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        description='Test the Innovation parser from the command line.'
    )
    parser.add_argument('command')
    args = parser.parse_args()
    if args.command == 'create':
        create_tables()
    elif args.command == 'delete':
        delete_tables()
    else:
        print("Run 'models.py create' to create database tables.")

