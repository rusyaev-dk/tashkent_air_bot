import datetime
import random
import string
from typing import List, Dict


def generate_random_id(length: int):
    """
    Generates random combination of symbols for questionnaire_id in database
    """

    symbols = string.ascii_lowercase + string.ascii_uppercase + string.digits
    return ''.join(random.choice(symbols) for _ in range(length))


def get_correct_update_run_time(now: datetime):
    update_run_time = None
    minutes = int(now.strftime("%M"))
    seconds = int(now.strftime("%S"))

    if minutes % 5 == 0 and seconds <= 5:
        pass

    elif minutes > 55:
        update_run_time = now.replace(hour=now.hour + 1, minute=0, second=0, microsecond=0)

    elif minutes % 5 != 0 or seconds > 5:
        minutes = (minutes // 5 + 1) * 5
        if minutes >= 60:
            update_run_time = now.replace(hour=now.hour + 1, minute=0, second=0, microsecond=0)
        else:
            update_run_time = now.replace(minute=minutes, second=0, microsecond=0)

    return update_run_time


def find_notification_in_list(notifications_list: List[Dict], hours: str):
    for notification in notifications_list:
        if notification.get("hours") == hours:
            return True
    return False


def compare_notifications_lists(
        list_1: List,
        list_2: List,
) -> bool:

    if len(list_1) != len(list_2):
        return False

    list_1 = sorted(list_1, key=lambda x: x.get("hours"))
    list_2 = sorted(list_2, key=lambda x: x.get("hours"))

    for i in range(len(list_1)):
        if list_1[i].get("hours") != list_2[i].get("hours"):
            return False
    return True
