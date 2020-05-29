from datetime import datetime, timedelta

from telegram import KeyboardButton, InlineKeyboardButton

import constants as c

default_board = [
    [KeyboardButton("/vreausaajut")],
    [KeyboardButton("/help"), KeyboardButton("/about")],
]

# This one is used during onboarding, to ask for the phone number
contact_keyboard = KeyboardButton(text=c.BTN_GET_PHONE, request_contact=True)

# this keyboard is sent to the volunteer along with each request for assistance
initial_responses = [
    [KeyboardButton("/Da")],
    [KeyboardButton("/Nu")],
]

eta_first_responses = [
    [
        InlineKeyboardButton("În 30min", callback_data="eta_30min"),
        InlineKeyboardButton("Într-o oră", callback_data="eta_1h"),
        InlineKeyboardButton("În 2 ore", callback_data="eta_2h"),
    ],
    [InlineKeyboardButton("Altă oră", callback_data="eta_later")],
    [InlineKeyboardButton("Anulează", callback_data="eta_never")],
]


def build_dynamic_keyboard_first_responses():
    """Build a dynamic keyboard that looks like `eta_first_responses`, but where the callback data contains
    timestamps that are N minutes in the future from now"""
    now = datetime.utcnow()
    timedelta(minutes=30)

    return [
        [
            InlineKeyboardButton(
                "În 30min", callback_data="eta_" + (now + timedelta(minutes=30)).strftime("%H:%M")
            ),
            InlineKeyboardButton(
                "Într-o oră", callback_data="eta_" + (now + timedelta(hours=1)).strftime("%H:%M")
            ),
            InlineKeyboardButton(
                "În 2 ore", callback_data="eta_" + (now + timedelta(hours=2)).strftime("%H:%M")
            ),
        ],
        [InlineKeyboardButton("Altă oră", callback_data="eta_later")],
        [InlineKeyboardButton("Anulează", callback_data="eta_never")],
    ]


def get_etas_today(time_from=None):
    """Construct a list of time options to choose from, starting with NOW, until the end of TODAY
    :param time_from: optional datetime, by default it is now"""
    time_from = time_from or datetime.utcnow()
    today = datetime.today().date()

    times = []
    step = timedelta(minutes=30)
    i = 1
    while True:
        new_entry = time_from + i * step
        times.append(new_entry)
        i += 1
        if new_entry.date() > today:
            break
    return times


def build_dynamic_keyboard(time_from=None):
    """Construct a keyboard with various time options to choose from
    :param time_from: optional datetime, by default it is now
    :returns: Telegram keyboard that looks like this:
    keyboard = [
        [InlineKeyboardButton("15:32", callback_data="eta_15:32")],
        [InlineKeyboardButton("16:02", callback_data="eta_16:02")],
        [InlineKeyboardButton("16:32", callback_data="eta_16:32")],
    ]
    """
    times = [item.strftime("%H:%M") for item in get_etas_today(time_from)]

    keyboard = []
    for entry in times:
        keyboard.append([InlineKeyboardButton(entry, callback_data="eta_" + entry)])
    return keyboard


if __name__ == "__main__":
    print(build_dynamic_keyboard())
    print(build_dynamic_keyboard_first_responses())
