import datetime
import random
import string


def generate_random_id(length: int, prefix: str = None):

    symbols = string.ascii_lowercase + string.ascii_uppercase + string.digits

    rand_id = ''.join(random.choice(symbols) for _ in range(length))
    if prefix:
        return prefix + rand_id
    return rand_id


def get_correct_update_run_time(now: datetime):
    update_run_time = None
    minutes = int(now.strftime("%M"))
    seconds = int(now.strftime("%S"))

    if minutes % 5 == 0 and seconds <= 5:
        update_run_time = now.replace(minute=now.minute)

    elif minutes > 55:
        update_run_time = now.replace(hour=now.hour + 1, minute=0, second=0, microsecond=0)

    elif minutes % 5 != 0 or seconds > 5:
        minutes = (minutes // 5 + 1) * 5
        if minutes >= 60:
            update_run_time = now.replace(hour=now.hour + 1, minute=0, second=0, microsecond=0)
        else:
            update_run_time = now.replace(minute=minutes, second=0, microsecond=0)

    return update_run_time
