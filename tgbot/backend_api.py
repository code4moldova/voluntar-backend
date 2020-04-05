"""This module is a standalone client for the backend API. It is meant to keep the logic of the Telegram bot
separated from the backend interaction, to avoid tight coupling. The Telegram bot will only use the functions
of the `Backender` class, without being aware of what these functions are doing underneath.

Keep this in mind as you update this file: any function that starts with an underscore _ is not expected to be
invoked by the Telegram bot. All the other functions are assumed to be used by others, so make sure their
prototype is not changed unless there is a good reason.

The easiest way to work on this client is to run `python backend_api.py`, adjusting the contents after
`if __name__ == "__main__"` - this way you can test it without touching any Telegram functionality whatsoever."""

import logging

import requests

log = logging.getLogger("back")


class Backender(object):
    def __init__(self, url, username, password):
        """Initialize the backend REST API client"""
        self.base_url = url
        self.username = username
        self.password = password

    def _get(self, url):
        """Function for internal use, that sends GET requests to the server
        :param url: str, this will be added to the base_url to which the request is sent"""
        res = requests.get(self.base_url + url, auth=(self.username, self.password))
        # log.debug('Got %s', res.status_code)
        if res.status_code == 200:
            return res

        raise ValueError("Bad response")

    # TODO
    def _post(self, payload, url=""):
        """Function for internal use, it sends POST requests to the server
        :param payload: what needs to be sent within the POST request
        :param url: str, this will be added to the base_url to which the request is sent"""
        requests.get(self.base_url + url, auth=(self.username, self.password))

    def get_request_details(self, request_id):
        """Retrieve the details of a request
        :param request_id: str, request id
        :returns: dict with the metadata"""
        response = self._get("beneficiary/filters/1/10?id=" + request_id)
        raw = response.json()

        # if there are no results, it means that such a request ID doesn't exist
        if raw["count"] == 0:
            raise KeyError

        # If we got this far, it means that the request exists and we can retrieve its details. Note that we
        # only take the first element, because we expect there to be a single request with that id
        return raw["list"][0]

    # TODO
    def link_chatid_to_volunteer(self, nickname, chat_id, phone):
        """Tell the backend that we've got a new bot user, along with their phone number, chat_id and nickname.
        :param nickname: optional str, Telegram nickname of the user, may be None if the nickname is not set
        :param chat_id: int, numerical chat_id that uniquely identifies the user's session with the bot in Telegram
        :param phone: str, phone number, full representation, e.g.:'+37379000000'"""
        log.debug("Link vol:%s to chat %s and tel %s", nickname, chat_id, phone)

    # TODO
    def upload_shopping_receipt(self, data, request_id):
        """Upload a receipt to the server, to document expenses handled by the volunteer on behalf of the
        beneficiary. Note that it is possible that a volunteer will send several photos that are linked to the same
        request in the system.
        :param data: bytearray, raw data corresponding to the image
        :param request_id: str, identifier of request"""
        log.debug("Send receipt (%i bytes) for req:%s", len(data), request_id)

    # TODO
    def relay_offer(self, request_id, volunteer_id, offer):
        """Notify the server that an offer to handle a request was provided by a volunteer. Note that this function
        will be invoked multiple times for the same request, as soon as each volunteer will send their response.
        :param request_id: str, identifier of request
        :param volunteer_id: str, volunteer identifier
        :param offer: TODO the offer indicates when the volunteer will be able to reach the beneficiary"""
        log.debug("Relay offer for req:%s from vol:%s -> %s", request_id, volunteer_id, offer)

    # TODO
    def update_request_status(self, request_id, status):
        """Change the status of a request, e.g., when a volunteer is on their way, or when the request was fulfilled.
        :param request_id: str, identifier of request
        :param status: TODO indicate what state it is in {new, assigned, in progress, done, something else...}"""
        log.debug("Set req:%s to: `%s`", request_id, status)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG, format="%(asctime)s %(levelname)5s %(name)5s - %(message)s"
    )

    # Here you can play around with the backend without involving any of the Telegram-related logic. Change these
    # credentials before running the demo
    url = "http://127.0.0.1:5000/api/"
    username = "testuser"
    password = "changethis"  # nosec

    b = Backender(url, username, password)
    result = b.get_request_details("5e84c10a9938cfffc0217ed1")
    log.info(result)
