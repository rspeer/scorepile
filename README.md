# scorepile.org - hosts and analyzes game logs from innovation.isotropic.org

scorepile.org is an archive of Innovation games played on
innovation.isotropic.org.

Do you want to help? Here are some things that could be done:

- Develop the parser
- Come up with ways to extract useful statistics from games
- Come up with meta-game "Achievements", find out who's achieved them, and
  display that on the Web

## Design decisions

I've used NoSQL databases in various projects, but the most important thing is
to use the right tool for the job. Here, we want to search a bunch of games
based on a wide variety of criteria, and there are relational properties
attached such as the mapping from player IDs to player names. I'm actually
reasonably convinced that SQL is the right tool, and PostgreSQL is the best
SQL.

scorepile.org is currently using super-cheap shared hosting at WebFaction,
because I don't want to pay too much for this site until it's worthwhile.
I could upgrade to dedicated hosting if shared hosting becomes a problem.

I use Python 3 because:

- It's more fun than Python 2
- I want to gain practical experience with Python 3
- It's good enough for Isotropic

I use Bottle as the web framework because it's simple and it's known to have
good Python 3 support.

scorepile.org is equivalent to innovation.scorepile.org so that:

- You can just change "isotropic" to "scorepile" in a game log URL and get
  scorepile's copy of it
- Someday I could put more stuff on scorepile.org, because it's an awesome
  domain name
