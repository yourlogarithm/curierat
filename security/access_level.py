from enum import Flag


class AccessLevel(Flag):
    CLIENT = 0
    COURIER = 1
    OFFICE = 2
    MODERATOR = 3
    ADMIN = 4
