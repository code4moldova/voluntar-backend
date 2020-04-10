import requests
import io
import base64
from .volunteer import sort_closest
from config import AJUBOT_HOST, AJUBOT_PORT, AJUBOT_RECEIPT_PATH
from PIL import Image
from flask import jsonify
from datetime import datetime
from models import Beneficiary, Volunteer
import logging
log = logging.getLogger("back")



BASE_URL = f'{AJUBOT_HOST}:{AJUBOT_PORT}'



def send_request(beneficiary):
    """Sends a POST request to telegram bot api for looking a volunteer
    :param beneficiary: Beneficiary, object of the beneficiary for whom a volunteer is being sought
    :return: if the response is success then will return a json as
        {
            "request_id": "5e88845adcc1e3b2786c311e",
            "beneficiary": "Jennifer Lopez",
            "address": "str. HappyStreet"
            "needs": "some beer",
            "gotSymptoms": false,
            "safetyCode": "bla bla bla",
            "phoneNumber": "+37312345678"
            "remarks": "No remarks"
            "volunteers": ["324354681651", "5168132468431"]
         },
         otherwise - {"error": "error message"}
    """
    beneficiary_id = str(beneficiary['id'])
    volunteers = [int(v['telegram_chat_id']) for v in sort_closest(beneficiary_id, 5, None).json['list'] if
                  'telegram_chat_id' in v]
    # todo: check if already sent or accepted other?
    # return volunteers
    if len(volunteers)>0:
        payload = {
            'request_id': beneficiary_id,
            'beneficiary': beneficiary.first_name + ' ' + beneficiary.last_name,
            'address': beneficiary.address,
            'needs': beneficiary.activity_types,
            'gotSymptoms': beneficiary.has_symptoms,
            'safetyCode': beneficiary.secret,
            'phoneNumber': beneficiary.phone,
            'remarks': beneficiary.remarks,
            'volunteers': volunteers
        }
        try:
            requests.post(f'{BASE_URL}/help_request', json=payload)
            return payload
        except Exception as error:
            # return str(-1)
            jsonify({"error": str(error)}), 400
            pass


def send_assign(beneficiary_id, volunteer_id):
    """Sends a POST request to telegram bot api to assign a request to a volunteer
    :param beneficiary_id: str, Beneficiary ID for whom will be performed a request
    :param volunteer_id: Volunteer ID who is going to perform a request
    :return: if the response is success then will return a json as {"request_id": "5e88845adcc1e3b2786c311e",
            "volunteer": "123456789", "time": "00:00"}, otherwise - {"error": "error message"}
    """

    volunteer = Volunteer.objects(id=volunteer_id).get()
    if "telegram_chat_id" in volunteer:
        time_s = '20:20'
        data = volunteer.clean_data()
        for i in data['offer_list']:
            if i['id'] == beneficiary_id:
                time_s = i['offer']
        payload = {
            'request_id': beneficiary_id,
            'volunteer': int(volunteer['telegram_chat_id']),
            'time': time_s# utc_short_to_user_short(time_s)#volunteer['availability_day']
        }
        log.info("ASSIGN req:%s to vol:%s", time_s, volunteer['telegram_chat_id'])
        try:
            requests.post(f'{BASE_URL}/assign_help_request', json=payload)
            return payload
        except Exception as error:
            jsonify({"error": str(error)}), 400


def save_receive(beneficiary_id, data):
    """Uploads and saves images of shopping receipts from telegram bot api
    :param beneficiary_id: str, Beneficiary ID for whom was done the request
    :param data: bytearray, raw data corresponding to the image of shopping receipt
    :return: if the response is success then will return a json as {"response": "success"},
            otherwise - {"error": "error message"}
    """
    try:
        image = Image.open(io.BytesIO(base64.b64decode(data.encode())))
        save_path = f'{AJUBOT_RECEIPT_PATH}/{beneficiary_id}_{"{:%Y%m%d_%H%M%S}".format(datetime.now())}.{image.format.lower()}'
        image.save(save_path)
        Beneficiary.objects(id=beneficiary_id).update(sent_foto=True, path_receipt=save_path)
        return jsonify({"response": "success"})
    except Exception as error:
        return jsonify({"error": str(error)}), 400


def send_cancel_request(beneficiary_id, volunteer_id):
    """Sends a POST request to telegram bot api to cancel the request to assist
    :param beneficiary_id: str, Beneficiary ID for whom is going to cancel a request
    :param volunteer_id: str, Volunteer's ID, who is going to be prevented about a request canceling
    :return: if the response is success then will return a json as {"request_id": "5e88845adcc1e3b2786c311e",
            "volunteer": "123456789"}, otherwise - {"error": "error message"}
    """
    volunteer = Volunteer.objects(id=volunteer_id).get()
    payload = {
        'request_id': beneficiary_id,
        'volunteer': volunteer['telegram_chat_id']
    }
    try:
        requests.post(f'{BASE_URL}/cancel_help_request', json=payload)
        return payload
    except Exception as error:
        return jsonify({"error": str(error)}), 400
