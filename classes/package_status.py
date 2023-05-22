from enum import Enum


class PackageStatus(str, Enum):
    Transit = 'transit'
    WaitingReceiver = 'waiting_receiver'
    WaitingSender = 'waiting_sender'
    ExtendedAwait = 'extended_await'
    Returning = 'returning'
    Delivered = 'delivered'
