from bottle import route, abort
from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options
from datetime import datetime, timedelta
import pytz
from scorepile.db import Session
from jinja2 import Environment, PackageLoader
from scorepile.dateutils import full_date
import os

BASE_PATH = os.path.dirname(__file__) or '.'
ENV = Environment(loader=PackageLoader('scorepile.web', 'templates'))
TEMPLATES = {
    'main_page': ENV.get_template('main_page.html'),
    'game_list': ENV.get_template('game_list.html')
}
PT = pytz.timezone('US/Pacific')

CACHE_OPTS = {
    'cache.type': 'file',
    'cache.data_dir': BASE_PATH + '/cache/data',
    'cache.lock_dir': BASE_PATH + '/cache/lock',
}
cache = CacheManager(**parse_cache_config_options(CACHE_OPTS))


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
def main_page():
    dates = []
    now = datetime.now(PT)
    for i in range(7):
        backdate = now - timedelta(days=i)
        dates.append({
            'url': '/games/' + backdate.strftime('%Y/%m/%d'),
            'title': full_date(backdate)
        })

    return TEMPLATES['main_page'].render(dates=dates)

