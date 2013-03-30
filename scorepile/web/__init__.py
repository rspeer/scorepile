from bottle import route
from datetime import datetime, timedelta
import pytz
from scorepile.models import Game, GamePlayer, Player
from scorepile.db import Session
from jinja2 import Environment, PackageLoader

ENV = Environment(loader=PackageLoader('scorepile.web', 'templates'))
TEMPLATES = {
    'game_list': ENV.get_template('game_list.html')
}

PT = pytz.timezone('US/Pacific')


class MiniSession:
    """
    A DB session that lasts for as long as a web request. Makes sure that
    nothing stays in memory between requests, because we're not paying for a
    server that lets us use a lot of memory.
    """
    def __enter__(self):
        self.session = Session()
        return self.session

    def __exit__(self, type, value, traceback):
        self.session.close()
        del self.session


@route('/')
def not_ready():
    return '<html>Not ready yet! Go help on <a href="http://github.com/rspeer/scorepile">GitHub</a>.</html>'

@route('/games')
@route('/games/')
def game_list():
    with MiniSession() as session:
        #yesterday = datetime.now(PT) - timedelta(days=1)
        yesterday = datetime(2013, 3, 18)
        games = Game.games_on_day(session, yesterday).all()
        return TEMPLATES['game_list'].render(title="Yesterday's games ({})".format(len(games)), games=games)
    
