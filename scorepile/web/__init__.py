from bottle import route

@route('/')
def not_ready():
    return '<html>Not ready yet! Go help on <a href="http://github.com/rspeer/scorepile">GitHub</a>.</html>'
