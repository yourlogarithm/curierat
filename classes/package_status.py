from enum import Enum


class PackageStatus(str, Enum):
    TRANSIT = 'transit'
    WAITING_RECEIVER = 'waiting_receiver'
    RETURNING = 'returning'
    DELIVERED = 'delivered'
