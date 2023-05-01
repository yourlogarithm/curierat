from enum import IntEnum


class AccessLevel(IntEnum):
    CLIENT = 0
    COURIER = 1
    OFFICE = 2
    MODERATOR = 3
    ADMIN = 4
