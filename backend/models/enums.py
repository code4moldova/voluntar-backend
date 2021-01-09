from enum import Enum


class UserRole(Enum):
    administrator = "administrator"
    coordinator = "coordinator"
    operator = "operator"


class WeekDay(Enum):
    monday = "monday"
    tuesday = "tuesday"
    wednesday = "wednesday"
    thursday = "thursday"
    friday = "friday"
    saturday = "saturday"
    sunday = "sunday"


class SpecialCondition(Enum):
    disability = "disability"
    deaf_mute = "deaf_mute"
    blind_weak_seer = "blind_weak_seer"


class RequestStatus(Enum):
    new = "new"
    confirmed = "confirmed"
    in_process = "in_process"
    canceled = "canceled"
    solved = "solved"
    archived = "archived"


class RequestType(Enum):
    warm_lunch = "Warm Lunch"
    grocery = "Grocery"
    medicine = "Medicine"
    invoices = "Pay invoices"
    transport = "Transport person"


class VolunteerRole(Enum):
    delivery = "delivery"
    copilot = "copilot"
    packing = "packing"
    supply = "supply"
    operator = "operator"


class VolunteerStatus(Enum):
    active = "active"
    inactive = "inactive"
    blacklist = "blacklist"


class Zone(Enum):
    botanica = "botanica"
    buiucani = "buiucani"
    centru = "centru"
    ciocana = "ciocana"
    riscani = "riscani"
    telecentru = "telecentru"
    suburbii = "suburbii"


class NotificationType(Enum):
    new_request = "new_request"
    canceled_request = "canceled_request"


class NotificationStatus(Enum):
    new = "new"
    seen = "seen"
    delete = "delete"
