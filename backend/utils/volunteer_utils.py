import re
import os

import phonenumbers

from config import MIN_PASSWORD_LEN
from models import Volunteer

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


def convert_phone_to_regional(phone):
    """ Converts given phone number from international format(+37300000000) into regional (without prefix +373).

    Parameters
    ----------
    phone : str
        Given value of phone number to convert.

    Returns
    -------
    str
        A string representing regional phone number.
    """
    return phonenumbers.parse(phone).national_number


def is_email(provided_string):
    """Checks if the given string is an email.

    Parameters
    ----------
    provided_string : str
        A string to be checked for similarity with email.

    Returns
    -------
    bool
        True if given string is an email, False otherwise.
    """
    email_regex = re.compile(r"[^@]+@[^@]+\.[^@]+")
    return re.match(email_regex, provided_string)


def validate_password(password):
    """Validates given password.

    Parameters
    ----------
    password : str
        A string representing password, to be verified.

    Raises
    -------
    AssertionError
        If password is shortly as constant MIN_PASSWORD_LEN from config.py.
    """
    assert len(password >= MIN_PASSWORD_LEN), f"Password is to short, min length is {MIN_PASSWORD_LEN}"


def exists_by_email(email):
    """Checks, if a volunteer with the given email, already exists in the database.

    Parameters
    ----------
    email : str
        Given email for validating.

    Raises
    -------
    AssertionError
        If volunteer with given email already exists in database.
    """
    assert not Volunteer.objects(email=email), "User with this email already exists"


def send_email(cluster_id, to):

    html = "<a href='{}/cluster/{}'>Detalii sarcina</a>".format(os.environ.get("URL_SITE"), cluster_id)

    message = Mail(from_email="moshnoi2000@gmail.com", to_emails=to, subject="Voluntar.md sarcina", html_content=html)

    try:
        sg = SendGridAPIClient(os.environ.get("API_KEY_SENDGRID"))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e)
        print(e.body)
        return False
    return True
