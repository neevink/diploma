import string
from random import choice

VALID_CHARACTERS = string.ascii_letters + string.digits
DEFAULT_LOCK_ID_LENGTH = 20


def new_unique_lock_id(valid_chars: str = VALID_CHARACTERS, length: int = DEFAULT_LOCK_ID_LENGTH):
    lock_id = []
    for _ in range(length):
        lock_id.append(choice(valid_chars))
    return ''.join(lock_id).encode()
