activate_this = '/home/rspeer/webapps/scorepile/env/bin/activate_this.py'
exec(compile(open(activate_this).read(), activate_this, 'exec'), dict(__file__=activate_this))
import sys

def application(environ, start_response):
    output = '<html>Not ready yet! Go help on <a href="http://github.com/rspeer/scorepile">GitHub</a>.</html>'

    response_headers = [
        ('Content-Length', str(len(output))),
        ('Content-Type', 'text/html'),
    ]

    start_response('200 OK', response_headers)

    return [output]
