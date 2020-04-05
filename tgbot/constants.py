from enum import Enum

VERSION = "0.0.1"  # follow SemVer conventions: https://semver.org/
URL = "code4md.com"

# Messages used in various phases of interaction
MSG_HELP = "Încearcă comanda /vreausaajut"
MSG_ABOUT = f"Ajubot v{VERSION}, {URL}"
MSG_STANDBY = "Mulțumesc! Te vom alerta când apar cereri noi."
MSG_THANKS_NOTHANKS = "Bine, te vom alerta când apar cereri noi."
MSG_ACK_TIME = "Bine, ora %s, "
MSG_COORDINATING = "coordonez cu alți voluntari."
MSG_PHONE_QUERY = "Te rog să ne transmiți numărul de telefon, pentru a finaliza înregistrarea."

MSG_REQUEST_ANNOUNCEMENT = "O persoană din %s are nevoie de:\n%s\nPoți ajuta?"

# Button labels
BTN_GET_PHONE = "Trimite numărul de telefon"


class State(Enum):
    EXPECTING_PHONE_NUMBER = 0
    ONBOARD_COMPLETE = 1
    REQUEST_SENT = 2
    REQUEST_TIME_NEGOTIATION = 3
    REQUEST_ASSIGNED = 4
    REQUEST_IN_PROGRESS = 5
    REQUEST_COMPLETED = 6
