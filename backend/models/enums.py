from enum import Enum


class Role(Enum):
    administrator = 'administrator'
    coordinator = 'coordinator'
    operator = 'operator'


class WeekDay(Enum):
    monday = 1
    tuesday = 2
    wednesday = 3
    thursday = 4
    friday = 5
    saturday = 6
    sunday = 7


class SpecialCondition(Enum):
    disability = 'disability'
    deaf_mute = 'deaf_mute'
    blind_weak_seer = 'blind_weak_seer'


class RequestStatus(Enum):
    new = 'new'
    confirmed = 'confirmed'
    in_process = 'in_process'
    canceled = 'canceled'
    solved = 'solved'
    archived = 'archived'


class VolunteerRole(Enum):
    delivery = 'delivery'
    copilot = 'copilot'
    packing = 'packing'
    supply = 'supply'
    operator = 'operator'


class VolunteerStatus(Enum):
    active = 'active'
    inactive = 'inactive'
    blacklist = 'blacklist'


class Zone(Enum):
    botanica = 'Botanica'
    buiucani = 'Buiucani'
    centru = 'Centru'
    ciocana = 'Ciocana'
    riscani = 'Riscani'
    telecentru = 'Telecentru'
    suburbii = 'Suburbii'


class NotificationType(Enum):
    new_request = 'new_request'
    canceled_request = 'canceled_request'


class NotificationStatus(Enum):
    new = 'new'
    seen = 'seen'
    delete = 'delete'
