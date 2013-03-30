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


@route('/')
def not_ready():
    return '<html>Not ready yet! Go help on <a href="http://github.com/rspeer/scorepile">GitHub</a>.</html>'

@route('/games')
@route('/games/')
def game_list():
    session = Session()
    #yesterday = datetime.now(PT) - timedelta(days=1)
    yesterday = datetime(2013, 3, 18)
    games = Game.games_on_day(session, yesterday).all()
    return TEMPLATES['game_list'].render(title="Yesterday's games ({})".format(len(games)), games=games)
    
