from datetime import datetime, timedelta


def midnight_before(dt):
    return datetime(dt.year, dt.month, dt.day, tzinfo=dt.tzinfo)


def midnight_after(dt):
    return midnight_before(dt) + timedelta(days=1)

