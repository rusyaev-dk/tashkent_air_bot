import random
import string


def generate_random_id(length: int, prefix: str = None):

    symbols = string.ascii_lowercase + string.ascii_uppercase + string.digits

    rand_id = ''.join(random.choice(symbols) for _ in range(length))
    if prefix:
        return prefix + rand_id
    return rand_id
