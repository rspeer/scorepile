from bs4 import BeautifulSoup
from bs4.element import Tag, NavigableString
import re
from pprint import pprint

# Enumerate some states
(START, NEXT_PLAYER, HAND, ACHIEVE, SCORE, ICONS, DONE) = range(7)

def close_images(line):
    """
    Work around an html.parser bug.
    """
    return re.sub(r'(<img (.*?)>)', r'\1</img>', line)

class GameParser:
    def __init__(self):
        self.state = START
        self.win_condition = None
        self.winner_keys = []
        self.players = {}
        self.cur_player = None

    @staticmethod
    def parse_file(filename):
        parser = GameParser()
        return parser.handle_stream(open(filename))

    def handle_stream(self, file):
        for line in file:
            line = line.strip()
            if line:
                self.handle_line(line)
            if self.state == DONE:
                return {
                    'win_condition': self.win_condition,
                    'nplayers': len(self.players),
                    'players': self.players
                }

    def handle_line(self, line):
        tree = BeautifulSoup(close_images(line))
        items = tree.contents

        if isinstance(items[0], Tag) and items[0].name == 'hr':
            self.state = DONE

        else:
            if self.state == START:
                # The first line contains the winner and win condition.
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
                pid = player['id']
                name = player.string
                pstate = make_player_state(name, pid)
                
                # Determine if this player won.
                pstate['winner'] = (key in self.winner_keys)

                # Store a reference to this player as 'p0', 'p1', or whatever.
                # Also remember that it's the current player.
                self.players[key] = self.cur_player = pstate
                self.state = HAND

            elif self.state == HAND:
                cards = tree.find_all('span', class_='card')
                card_names = [card.string for card in cards]
                self.cur_player['data']['cards'] = card_names
                self.state = ACHIEVE

            elif self.state == ACHIEVE:
                achieved = tree.find_all('span')
                ach_names = [ach.string.split()[0] for ach in achieved]
                self.cur_player['data']['achievements'] = ach_names
                self.state = SCORE

            elif self.state == SCORE:
                score_text = tree.find('b').string
                self.cur_player['data']['score'] = int(score_text[1:-1])
                self.state = ICONS

            elif self.state == ICONS:
                if len(tree.find_all('img')) == 6:
                    strings = [item for item in items
                               if isinstance(item, NavigableString)]
                    icons = [int(string.strip()) for string in strings]
                    self.cur_player['data']['icons'] = icons
                    self.state = NEXT_PLAYER

        print(items)

def make_player_state(name, pid):
    return {
        'name': name,
        'pid': pid,
        'winner': None,
        'data': {}
    }

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        description='Test the Innovation parser from the command line.'
    )
    parser.add_argument('filename')
    args = parser.parse_args()
    result = GameParser.parse_file(args.filename)
    pprint(result)
