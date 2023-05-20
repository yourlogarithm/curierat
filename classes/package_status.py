from enum import Enum


class PackageStatus(str, Enum):
    Transit = 'transit'
    WaitingReceiver = 'waiting_receiver'
    Returning = 'returning'
    Delivered = 'delivered'
