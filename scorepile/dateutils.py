from datetime import datetime, timedelta
import pytz

# All timestamps on Isotropic are in Pacific time.
# During the DST transition when this is ambiguous, the timestamps are
# ambiguous too. So let's standardize on using PT throughout scorepile.
PT = pytz.timezone('America/Los_Angeles')
UTC = pytz.timezone('UTC')


def midnight_before(dt):
    return datetime(dt.year, dt.month, dt.day, tzinfo=dt.tzinfo)


def midnight_after(dt):
    return midnight_before(dt) + timedelta(days=1)


def friendly_date(dt):
    if dt.tzinfo is None:
        dt = UTC.localize(dt).astimezone(PT)
    now = datetime.now(PT)
    diff = dt - midnight_before(now)
    days = diff.days

    if days >= 0:
        return 'today'
    elif days == -1:
        return 'yesterday'
    elif days >= -4:
        # express it as the day of the week
        return dt.strftime('%A')
    else:
        return full_date(dt)


def friendly_time(dt):
    if dt.tzinfo is None:
        dt = UTC.localize(dt).astimezone(PT)

    time = datetime.strftime(dt, '%I:%M %p').lstrip('0')
    tz = dt.tzname()
    return "{} ({})".format(time, tz)


def full_date(dt):
    if dt.tzinfo is None:
        dt = UTC.localize(dt)
    now = datetime.now(PT)
    
    date_in_year = dt.strftime('%A, %B %d').replace(' 0', ' ')
    if dt.year == now.year:
        return date_in_year
    else:
        return '{}, {}'.format(date_in_year, dt.year)

