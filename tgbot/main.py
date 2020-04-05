import logging
import sys
import os
from tempfile import NamedTemporaryFile

from telegram.ext import (
    Updater,
    Filters,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    # PicklePersistence,  # TODO doesn't propagate updates immediately, ask the lib maintainers why
    DictPersistence,
)
from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup
from telegram.ext.dispatcher import run_async


import constants as c
import keyboards as k
import restapi
from backend_api import Backender

log = logging.getLogger("ajubot")


class Ajubot:
    def __init__(self, bot, backend):
        """Constructor
        :param bot: instance of Telegram bot object
        :param backend: instance of a Backender object, responsible for dealing with the Covid server"""
        self.bot = bot
        self.backend = backend
        self.rest = restapi.BotRestApi(
            self.hook_request_assistance, self.hook_cancel_assistance, self.hook_assign_assistance,
        )

        # this will contain incoming assistance requests, the key is the requestID and the value is its payload
        self.requests = {}

    def serve(self):
        """The main loop"""
        log.info("Starting REST API in separate thread")

        # NOTE: The bandit security checker will rightfully complain that we're binding to all interfaces.
        # TODO discuss this detail once we have a better idea about the deployment environment
        restapi.run_background(self.rest, "0.0.0.0", 5001)  # nosec

        log.info("Starting bot handlers")
        self.init_bot()
        self.bot.start_polling()
        self.bot.idle()

    @staticmethod
    def get_params(raw):
        """Retrieve the parameters that were transmitted along with the
        command, if any.
        :param raw: str, the raw text sent by the user"""
        parts = raw.split(" ", 1)
        return None if len(parts) == 1 else parts[1]

    @staticmethod
    def on_bot_start(update, context):
        """Send a message when the command /start is issued."""
        user = update.effective_user
        # TODO add this to some local storage, maybe sqlite?
        log.info(
            f"ADD {user.username}, {user.full_name}, @{update.effective_chat.id}, {user.language_code}"
        )
        update.message.reply_text(f"Bine ai venit, {user.username or user.full_name}.")

        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=c.MSG_PHONE_QUERY,
            reply_markup=ReplyKeyboardMarkup([[k.contact_keyboard]], one_time_keyboard=True),
        )

        # set some context data about this user, so we can rely on this later
        context.user_data["state"] = c.State.EXPECTING_PHONE_NUMBER

    @staticmethod
    def on_bot_help(update, context):
        """Send a message when the command /help is issued."""
        update.message.reply_text(c.MSG_HELP)

    @staticmethod
    def on_bot_about(update, context):
        """Send a message when the command /about is issued."""
        update.message.reply_text(c.MSG_ABOUT)

    @staticmethod
    def on_bot_offer_to_help(update, context):
        """This is invoked when a volunteer explicitly tells us they are open for new requests."""
        # TODO consider notifying the backend about it
        update.message.reply_text(c.MSG_STANDBY)

    @staticmethod
    def on_bot_error(update, context):
        """Log Errors caused by Updates."""
        log.warning('Update "%s" caused error "%s"', update, context.error)

    @staticmethod
    def on_status(update, context):
        """Invoked when the user sends the /status command. At the moment this is only intended for debugging
        purposes, but it may be handy if the user has a queue of multiple requests"""
        current_state = context.user_data["state"]
        current_request = context.user_data.get("current_request", None)
        message = f"State: {current_state}\nRequest: {current_request}"

        context.bot.send_message(chat_id=update.message.chat_id, text=message)

    def init_bot(self):
        dispatcher = self.bot.dispatcher

        dispatcher.add_handler(CommandHandler("start", self.on_bot_start))
        dispatcher.add_handler(CommandHandler("help", self.on_bot_help))
        dispatcher.add_handler(CommandHandler("about", self.on_bot_about))
        dispatcher.add_handler(CommandHandler("vreausaajut", self.on_bot_offer_to_help))
        dispatcher.add_handler(CommandHandler("status", self.on_status))

        dispatcher.add_handler(CommandHandler("Da", self.on_accept))
        dispatcher.add_handler(CommandHandler("Nu", self.on_reject))

        # dispatcher.add_handler(CallbackQueryHandler(self.negotiate_time))
        dispatcher.add_handler(CallbackQueryHandler(self.negotiate_time, pattern="^eta.*"))

        dispatcher.add_handler(MessageHandler(Filters.photo, self.on_photo))
        dispatcher.add_handler(MessageHandler(Filters.contact, self.on_contact))
        dispatcher.add_error_handler(self.on_bot_error)

    def on_reject(self, update, _context):
        """Invoked when the user presses `No` after receiving a request for help"""
        self.send_message(update.message.chat_id, c.MSG_THANKS_NOTHANKS)

    def on_accept(self, update, _context):
        """Invoked when a user presses `Yes` after receiving a request for help"""
        self.bot.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Alege timpul",
            reply_markup=InlineKeyboardMarkup(k.build_dynamic_keyboard_first_responses()),
        )

    def negotiate_time(self, update, context):
        chat_id = update.effective_chat.id
        response_code = update.callback_query["data"]  # eta_later, eta_never, eta_20:45, etc.
        log.info(f"Offer @{update.effective_chat.id} @{response_code}")

        if response_code == "eta_never":
            # the user pressed the button to say they're cancelling their offer
            self.send_message(chat_id, c.MSG_THANKS_NOTHANKS)
            self.bot.persistence.user_data[chat_id]["reviewed_request"] = None

        elif response_code == "eta_later":
            # Show them more options in the interactive menu
            self.bot.bot.send_message(
                chat_id=chat_id,
                text="Alege timpul",
                reply_markup=InlineKeyboardMarkup(k.build_dynamic_keyboard()),
            )
        else:
            # This is an actual offer, ot looks like `eta_20:40`, extract the actual timestamp
            offer = response_code.split("_")[-1]

            # tell the backend about it
            request_id = self.bot.persistence.user_data[chat_id]["reviewed_request"]
            self.backend.relay_offer(request_id, chat_id, offer)

            # tell the user that this is now processed by the server
            self.send_message(chat_id, (c.MSG_ACK_TIME % offer) + c.MSG_COORDINATING)

    def on_contact(self, update, context):
        """This is invoked when the user sends us their contact information, which includes their phone number."""
        user = update.effective_user
        phone = update.message.contact.phone_number
        log.info(
            f"TEL from {user.username}, {user.full_name}, @{update.effective_chat.id}, {phone}"
        )

        # Here's an example of what else you can find in update['message'].contact.to_dict()
        # {'phone_number': '+4500072470000', 'first_name': 'Alex', 'user_id': 253150000}
        # And some user-related details in update.effective_user.to_dict()
        # {'first_name': 'Alex', 'id': 253150000, 'is_bot': False, 'language_code': 'en', 'username': 'ralienpp'}

        # Tell the backend about it, such that from now on it knows which chat_id corresponds to this user
        self.backend.link_chatid_to_volunteer(user.username, update.effective_chat.id, phone)

        # Acknowledge receipt and tell the user that we'll contact them when new requests arrive
        update.message.reply_text(c.MSG_STANDBY)

        # Mark the user as 'onboarded
        context.user_data["state"] = c.State.ONBOARD_COMPLETE

    def on_photo(self, update, context):
        """Invoked when the user sends a photo to the bot. In our case, photos are always shopping receipts. Keep in
        mind that there could be multiple photos in a message."""
        user = update.effective_user
        photo_count = len(update.message.photo)
        log.info(
            f"PHOTO from {user.username}, {user.full_name}, @{update.effective_chat.id}, #{photo_count}"
        )

        # Process each photo
        for entry in update.message.photo:
            raw_image = entry.get_file().download_as_bytearray()

            # At this point the image is in the memory
            with NamedTemporaryFile(delete=False, prefix=update.effective_chat.id) as f:
                f.write(raw_image)
                log.debug("Image written to %s", f.name)

            self.backend.upload_shopping_receipt(raw_image, context.user_data["current_request"])

    @run_async
    def hook_request_assistance(self, data):
        """This will be invoked by the REST API when a new request for
        assistance was received from the backend.
        :param data: dict, the format is defined in `assistance_request`, see readme"""
        request_id = data["request_id"]
        log.info("NEW request for assistance %s", request_id)
        volunteers_to_contact = data["volunteers"]

        needs = ""
        for item in data["needs"]:
            needs += f"- {item}\n"

        assistance_request = c.MSG_REQUEST_ANNOUNCEMENT % (data["address"], needs)

        for chat_id in volunteers_to_contact:
            if chat_id not in self.bot.persistence.user_data:
                log.debug("User %s hasn't added the bot to their contacts, skipping.", chat_id)
                continue

            current_state = self.bot.persistence.user_data[chat_id].get("state", None)

            if current_state in [c.State.REQUEST_IN_PROGRESS, c.State.REQUEST_ASSIGNED]:
                log.debug("Vol%s is already working on a request, skippint")
                continue

            self.bot.bot.send_message(
                chat_id=chat_id,
                text=assistance_request,
                reply_markup=ReplyKeyboardMarkup(k.initial_responses, one_time_keyboard=True),
            )

            # update this user's state and keep the request_id as well, so we can use it later
            self.bot.persistence.user_data[chat_id]["state"] = c.State.REQUEST_SENT
            self.bot.persistence.user_data[chat_id]["reviewed_request"] = request_id

        self.bot.persistence.bot_data[request_id] = data
        self.bot.persistence.flush()  # just in case, to make sure all the data are persisted

    @run_async
    def hook_cancel_assistance(self, raw_data):
        """This will be invoked by the REST API when a new request for
        assistance was CANCELED from the backend.
        :param raw_data: TODO: discuss payload format, see readme"""
        log.info("CANCEL request for assistance")

    @run_async
    def hook_assign_assistance(self, raw_data):
        """This will be invoked by the REST API when a new request for
        assistance was ASSIGNED to a specific volunteer.
        :param raw_data: TODO: discuss payload format, see readme"""
        volunteer = "hardcoded for now"
        log.info("ASSIGN request for assistance to %s", volunteer)
        # self.send_message("")

    @run_async
    def send_message(self, chat_id, text):
        """Send a message to a specific chat session
        :param chat_id: int, chat identifier
        :param text: str, the text to be sent to the user"""
        self.bot.bot.sendMessage(chat_id=chat_id, text=text)
        log.info("Send msg @%s: %s..", chat_id, text[:20])


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG, format="%(asctime)s %(levelname)5s %(name)5s - %(message)s"
    )

    # you might want to re-enable these two lines if you really need to debug the bot's internals
    logging.getLogger("telegram").setLevel(logging.WARNING)
    logging.getLogger("JobQueue").setLevel(logging.WARNING)

    log.info("Starting Ajubot v%s", c.VERSION)

    try:
        token = os.environ["TELEGRAM_TOKEN"]
        covid_backend_url = os.environ["COVID_BACKEND"]
        covid_backend_user = os.environ["COVID_BACKEND_USER"]
        covid_backend_pass = os.environ["COVID_BACKEND_PASS"]
    except KeyError as key:
        sys.exit(f"Set {key} environment variable before running the bot")

    covid_backend = Backender(covid_backend_url, covid_backend_user, covid_backend_pass)

    # this will be used to keep some state-related info in a file that survives across bot restarts
    pickler = DictPersistence()
    # NOTE: the pickled persistence layer doesn't seem to propagate changes instantly, TODO find out why
    # pickler = PicklePersistence("state.bin")

    bot = Updater(token=token, use_context=True, persistence=pickler)
    ajubot = Ajubot(bot, covid_backend)

    try:
        ajubot.serve()
    except KeyboardInterrupt:
        log.debug("Interactive quit")
        sys.exit()
    finally:
        log.info("Quitting")
