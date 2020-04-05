import logging
from threading import Thread
import json

from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import BadRequest, MethodNotAllowed, HTTPException

log = logging.getLogger("rest")


class BotRestApi(object):
    def __init__(self, help_request_handler, cancel_request_handler, assign_request_handler):
        """Initialize the REST API
        :param help_request_handler: callable, a function that will be invoked when a new request for assistance arrives
        :param cancel_request_handler: callable, will be invoked when a request for assistance was cancelled
        :param assign_request_handler: callable, will be invoked when a request for assistance was assigned to someone"""
        self.help_request_handler = help_request_handler
        self.cancel_request_handler = cancel_request_handler
        self.assign_request_handler = assign_request_handler
        self.form = open("res/static/index.html", "rb").read()
        self.url_map = Map(
            [
                Rule("/", endpoint="root"),
                Rule("/help_request", endpoint="help_request"),
                Rule("/cancel_help_request", endpoint="cancel_help_request"),
                Rule("/assign_help_request", endpoint="assign_help_request"),
            ]
        )

    def dispatch_request(self, request):
        adapter = self.url_map.bind_to_environ(request.environ)
        try:
            endpoint, values = adapter.match()
            return getattr(self, "on_" + endpoint)(request, **values)
        except HTTPException as e:
            return e

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = self.dispatch_request(request)
        return response(environ, start_response)

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)

    def on_root(self, request):
        """Called when the / page is opened, it provides a form where you can manually send a JSON,
        as if it came from the backend server"""
        return Response(self.form, content_type="text/html")

    def on_help_request(self, request):
        """Called when a fixer used the front-end to add a new request to the system, and the system is looking for
        a volunteer to assist the person in need"""
        if request.method == "GET":
            return MethodNotAllowed()

        if request.method == "POST":
            try:
                data = json.loads(request.get_data())
            except json.decoder.JSONDecodeError:
                return BadRequest("Request malformed")

            # if we got this far, it means we're ok, so we invoke the function that does the job
            # and pass it the input parameters
            self.help_request_handler(data)
            return Response("Request handled")

    def on_cancel_help_request(self, request):
        """Called when a fixer notifies a volunteer that the request to assist has been cancelled"""
        if request.method == "GET":
            return MethodNotAllowed()

        if request.method == "POST":
            log.debug("Got cancel request: `%s`", request.form)
            if False:
                # TODO verify if the payload has all the required data
                # TODO define parameters in the data
                # do some processing, if there are any issues, return an error
                return BadRequest("Request malformed")

            # if we got this far, it means we're ok, so we invoke the function that does the job
            # and pass it the input parameters
            self.cancel_request_handler(request.form)
            return Response("Request handled")

    def on_assign_help_request(self, request):
        """Called when a fixer notifies a volunteer that the request to assist has been assigned to them"""
        if request.method == "GET":
            return MethodNotAllowed()

        if request.method == "POST":
            log.debug("Got assign request: `%s`", request.form)
            if False:
                # TODO verify if the payload has all the required data
                # TODO define parameters in the data
                # do some processing, if there are any issues, return an error
                return BadRequest("Request malformed")

            # if we got this far, it means we're ok, so we invoke the function that does the job
            # and pass it the input parameters
            self.assign_request_handler(request.form)
            return Response("Request handled")


def run_background(app, interface="127.0.0.1", port=5000):
    """Run the WSGI app in a separate thread, to make integration into
    other programs (that take over the main loop) easier"""
    from werkzeug.serving import run_simple

    t = Thread(target=run_simple, args=(interface, port, app), name="rest")
    t.daemon = True  # so that it dies when the main thread dies
    t.start()
    return t


def dummy_message(chat_id, text):
    """Sample of a function that will be invoked by the REST API
    when a message is received via POST. Normally, this would call
    a function that uses Telegram to send a message to a real user"""
    log.info("You want to send %s to chat=%s", text, chat_id)


if __name__ == "__main__":
    from werkzeug.serving import run_simple

    interface = "127.0.0.1"
    port = 5000
    application = BotRestApi(dummy_message)

    run_simple(interface, port, application, use_debugger=True, use_reloader=True)
