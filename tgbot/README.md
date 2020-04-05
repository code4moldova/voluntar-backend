# Telegram bot that connects volunteers to beneficiaries

- See `doc/chat_interaction.svg` to get an idea of the workflow
- Code derived from https://github.com/roataway/telegram-bot, it provides examples of stateful interactions

## The big picture

```
                                                                          (start here)

                                                                      +--------------------+
                                                                      |    pool of fixers  |
                                                                      |  F1, F2, .. Fn     |
                                                                      +--+-----------------+
                                                                         |
                                                                         |  the fixer uses the UI to
                                                                         |  add new help requests
                                                                         |  to the system
+--------------+          +--------------------------------+             |
|              |  notify  |                                |         +---v---------------+
|   pool of    |  and     |   +-----------------+          +         |    frontend       |
|   volunteers |  interact|   |   Telegram bot  |     feedack via    |                   |
|              <-------------->                 |     REST API       +-------------------+
|   Vol_1      |          |   |                 +----------+----+             |new
|   Vol_2      |          |   +-----^-----------+          |    |             |request
|   ..         |          |         |                      |    |    +--------v----------+
|   Vol_n      |          |         |  notify              +    +---->     backend       |
|              |          |         |                notify bot      |                   |
|              |          |   +-----+-----------+    about a new  +--+                   |
+--------------+          |   |   REST API      |    help request |  +-------------------+
                          |   |                 <----------+------+
                          |   |                 |          |
                          |   +-----------------+          |
                          |                                |
                          |                                |
                          |                 (this repo)    |
                          +--------------------------------+

```

Legend:

- `backend` - a running instance of https://github.com/code4moldova/covid19md-voluntari-server
- `REST API` is invoked by the backend to notify the bot about new requests for assistance. This eliminates the need for
the bot to continuously poll the backend for new requests.

## Endpoints

The following endpoints are used for interaction between the backend and the Telegram bot:

    [done] backend->bot: notify bot about a new request for assistance
    [done] backend->bot: notify the specific volunteer that they are responsible for a request
    [done] backend->bot: notify the specific volunteer that a request assigned to them was cancelled}
    - bot->backend: notify about offers from volunteers about a specific requestID
    - bot->backend: volunteer is on their way
    - bot->backend: mission accomplished
    - bot->backend: send the receipt
    - bot->backend: exit survey
    
    
## Payloads

Payload sample `assistance_request`:

    {
        "request_id": "fe91e4b6-e902-4d03-8500-d058673cb9bd",
        "beneficiary": "Martina Cojocaru",
        "address": "str. 31 August",
        "needs": ["Medicamente", "Produse alimentare"],
        "gotSymptoms": false,
        "safetyCode": "Izvor-45",
        "phoneNumber": "+373 777 77 777",
        "remarks": ["Nu lucreaza ascensorul", "Are caine rau"],
        "volunteers": ["chat_id1", "chat_id2", "chat_idN"]
      }



## Bot's state
Some information is stored in a persistent context that survives bot restarts. This information is needed to keep track
of entities throughout their lifecycle. The state is a dictionary.

### User related

- `state` - `{EXPECTING_PHONE_NUMBER, ONBOARD_COMPLETE ...}`
- `current_request` - a string with the ID of the request that is currently handled by this user. Can be `None` if no
request is currently handled.




## How to run it

1. Talk to @BotFather to register your bot and get a token, as described here: https://core.telegram.org/bots#6-botfather
2. Install dependencies from `requirements.txt` using `virtualenv` or `pipenv`
3. Set the `TELEGRAM_TOKEN` environment variable to the token, e.g. `export TELEGRAM_TOKEN=1123test`
4. Set the environment variables for connecting to the backend: `COVID_BACKEND` (e.g. `http://127.0.0.1:5000/api/`),
`COVID_BACKEND_USER`, `COVID_BACKEND_PASS`
5. Run `python main.py`

Optionally, you can open http://localhost:5001 to send an example of a payload, simulating an actual request that came
from the backend.


# How to contribute

1. Run ``make autoformat`` to format all ``.py`` files
2. Run ``make verify`` and examine the output, looking for issues that need to be addressed
3. Open a pull request with your changes


# How to use the Docker image

1. Build it first: `docker build -t covid-tg-bot .`. Run `docker images` to ensure it is in the list.
2. Run it with: `docker run --rm -it -p 5001:5001 -e TELEGRAM_TOKEN='----replace-token-here' -e COVID_BACKEND=http://127.0.0.1:5000/ e COVID_BACKEND_USER=admin e COVID_BACKEND_PASS=secret covid-tg-bot` (adjust to
taste, for example you might want to remove `--rm`)