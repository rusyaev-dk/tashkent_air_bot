import random
import string
from typing import List, Dict


def generate_random_id(length: int):
    """
    Generates random combination of symbols for questionnaire_id in database
    """

    symbols = string.ascii_lowercase + string.ascii_uppercase + string.digits
    return ''.join(random.choice(symbols) for _ in range(length))


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
