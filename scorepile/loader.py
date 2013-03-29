__package__ = 'scorepile'
import scorepile
import os
from .db import Session
from .parser import GameParser
from .models import Game


def load_game(filename):
    parsed = GameParser.parse_file(filename)
    session = Session()
    game = Game.create(parsed, session)

def load_dir(path):
    path = path.rstrip('/')
    for filename in os.listdir(path):
        if filename.endswith('.html'):
            print(filename)
            load_game(path + '/' + filename)

# This file can be run as a script from the command line.
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        description='Load a directory of game logs into the database.'
    )
    parser.add_argument('dir')
    args = parser.parse_args()
    load_dir(args.dir)
