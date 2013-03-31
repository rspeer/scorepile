from bottle import route, abort, request
from scorepile.web import PT, TEMPLATES, cache, MiniSession
from datetime import datetime, timedelta
from scorepile.models import Game, Player
from scorepile.dateutils import friendly_date, full_date

@route('/games')
@route('/games/')
def game_list_yesterday():
    yesterday = datetime.now(PT) - timedelta(days=1)
    return game_list_on_date(yesterday)


@route('/games/<year>/<month>/<day>')
@route('/games/<year>/<month>/<day>/')
def game_list_interpret_date(year, month, day):
    try:
        year = int(year)
        month = int(month)
        day = int(day)
    except ValueError:
        abort(404)

    date = PT.localize(datetime(year, month, day))
    return game_list_on_date(date)


@cache.cache('games_by_day')
def game_list_on_date(date):
    title = "Games played {}".format(full_date(date))
    with MiniSession() as session:
        games = Game.games_on_day(session, date).all()
        return TEMPLATES['game_list'].render(title=title, games=games)


@route('/player/id/<iso_id>')
def player_by_id(iso_id):
    with MiniSession() as session:
        player = Player.get_by_iso_id(session, iso_id)
        if player is None:
            abort(404)
        else:
            return game_list_for_player(player)


@route('/player/name/<name>')
def player_by_name(name):
    with MiniSession() as session:
        player = Player.get_by_name(session, name)
        if player is None:
            abort(404)
        else:
            return game_list_for_player(player)
        

@route('/search')
def player_search():
    name = request.params.get('player')
    if not name:
        return TEMPLATES['no_results'].render(name='')
    else:
        with MiniSession() as session:
            player = Player.get_by_name(session, name)
            if player is None:
                return TEMPLATES['no_results'].render(name=name)
            else:
                return game_list_for_player(player)


@cache.cache('games_by_player')
def game_list_for_player(player):
    title = "Player: {}".format(player.name)
    with MiniSession() as session:
        games = player.played_games(session)
        return TEMPLATES['game_list'].render(title=title, games=games)

