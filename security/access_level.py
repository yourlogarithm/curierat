from enum import Flag


class AccessLevel(Flag):
    CLIENT = 0
    COURIER = 1
    OFFICE = 2
    ADMIN = 3
