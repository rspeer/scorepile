# boilerplate to activate a virtualenv
activate_this = '/home/rspeer/webapps/scorepile/env/bin/activate_this.py'
exec(compile(open(activate_this).read(), activate_this, 'exec'), dict(__file__=activate_this))

# bottle loading code
import os
os.chdir(os.path.dirname(__file__))
import bottle
from scorepile import web
from scorepile.web import game_list
application = bottle.default_app()

