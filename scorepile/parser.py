from bs4 import BeautifulSoup
from bs4.element import Tag, NavigableString
import pytz
import re
import time
from datetime import datetime
from pprint import pprint
from scorepile.dateutils import PT

# Enumerate some states
(START, NEXT_PLAYER, HAND, ACHIEVE, SCORE, ICONS, DONE) = range(7)


def close_images(line):
    "Work around an html.parser bug."
    return re.sub(r'(<img (.*?)>)', r'\1</img>', line)


class GameParser:
    """
    A state-based parser that extracts basic information from an Innovation
    game log.

    Because the GameParser accumulates state, a new GameParser should be
    created for each game. The best way to use it is the static method
    `GameParser.parse_file()`, which takes in a filename, creates a
    GameParser, and returns the result of parsing that file.
    """

    def __init__(self):
        self.state = START
        self.game_id = None
        self.win_condition = None
        self.winner_keys = []
        self.players = {}
        self.cur_player = None
        self.cardset = 'base'

    @staticmethod
    def parse_file(filename):
        parser = GameParser()
        return parser.handle_file(filename)

    @staticmethod
    def parse_time(timestr):
        stime = time.strptime(timestr, '%Y%m%d-%H%M%S')
        timestamp = datetime.fromtimestamp(time.mktime(stime), PT)
        return timestamp

    def handle_file(self, filename):
        file = open(filename)
        _before, sep, after = filename.partition('/gamelog/')
        url = sep + after

        # Extract the game's timestamp from the URL.
        timestr = '-'.join(url.split('-')[1:3])
        timestamp = GameParser.parse_time(timestr)


        for line in file:
            line = line.strip()
            if line:
                self.handle_line(line)
            if self.state == DONE:
                return {
                    'game_id': self.game_id,
                    'win_condition': self.win_condition,
                    'nplayers': len(self.players),
                    'players': self.players,
                    'url': url,
                    'timestamp': timestamp,
                    'cardset': self.cardset
                }

    def handle_line(self, line):
        tree = BeautifulSoup(close_images(line))
        items = tree.contents

        if isinstance(items[0], Tag) and items[0].name == 'hr':
            self.state = DONE

        else:
            if self.state == START:
                # The first line contains the game ID, winner, and win condition.
                title = tree.find('title').string
                before, _, game_id_str = title.partition('#')
                assert before == 'Innovation Game '
                self.game_id = int(game_id_str)

                win = tree.find('pre')
                winners = win.find_all('span')
                for winner in winners:
                    self.winner_keys.append(winner['class'][0])
                condition_text = win.contents[-1].strip()
                _wins, _by, condition = condition_text.partition(' by ')
                self.win_condition = condition.rstrip('!')
                self.state = NEXT_PLAYER

            elif self.state == NEXT_PLAYER:
                # Set up an object with basic information about the player.
                player = tree.find('span')
                key = player['class'][0]
                iso_id = player.get('id')
                name = player.string
                pstate = make_player_state(name, iso_id)
                
                # Determine if this player won.
                pstate['winner'] = (key in self.winner_keys)

                # Store a reference to this player as 'p0', 'p1', or whatever.
                # Also remember that it's the current player.
                self.players[key] = self.cur_player = pstate
                self.state = HAND

            elif self.state == HAND:
                # Get the contents of the player's initial hand.
                if 'age e' in line:
                    self.cardset = 'echoes'

                cards = tree.find_all('span', class_='card')
                card_names = [card.string for card in cards]
                self.cur_player['data']['cards'] = card_names
                self.state = ACHIEVE

            elif self.state == ACHIEVE:
                # Get the list of achievements this player claimed.
                achieved = tree.find_all('span')
                ach_names = [ach.string.split()[0] for ach in achieved]
                self.cur_player['data']['achievements'] = ach_names
                self.state = SCORE

            elif self.state == SCORE:
                # Get the player's final score.
                score_text = tree.find('b').string
                self.cur_player['data']['score'] = int(float(score_text[1:-1]))
                self.state = ICONS

            elif self.state == ICONS:
                # Get the player's final icon counts.
                if len(tree.find_all('img')) == 6:
                    strings = [item for item in items
                               if isinstance(item, NavigableString)]
                    icons = [int(string.strip()) for string in strings]
                    self.cur_player['data']['icons'] = icons
                    self.state = NEXT_PLAYER


def make_player_state(name, iso_id):
    """
    A basic data structure for tracking per-player information.
    """
    return {
        'name': name,
        'iso_id': iso_id,
        'winner': None,
        'data': {}
    }


# This file can be run as a script from the command line.
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        description='Test the Innovation parser from the command line.'
    )
    parser.add_argument('filename')
    args = parser.parse_args()
    result = GameParser.parse_file(args.filename)
    pprint(result)
