import requests
import io
import base64
from .volunteer import sort_closest
from config import AJUBOT_HOST, AJUBOT_PORT, AJUBOT_RECEIPT_PATH
from PIL import Image
from flask import jsonify
from datetime import datetime
from models import Beneficiary

BASE_URL = f'{AJUBOT_HOST}:{AJUBOT_PORT}'


def send_request(beneficiary):
    beneficiary_id = str(beneficiary['id'])
    volunteers = [int(v['telegram_chat_id']) for v in sort_closest(beneficiary_id, 5, None).json['list'] if 'telegram_chat_id' in v]
    #todo: check if already sent or accepted other?
    #return volunteers
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
            #return str(-1)
            return str(error)
            pass



def save_receive(beneficiary_id, data):
    try:
        image = Image.open(io.BytesIO(base64.b64decode(data.encode())))
        save_path = f'{AJUBOT_RECEIPT_PATH}/{beneficiary_id}_{"{:%Y%m%d_%H%M%S}".format(datetime.now())}.{image.format.lower()}'
        image.save(save_path)
        Beneficiary.objects(id=beneficiary_id).update(sent_foto=True, path_receipt=save_path)
        return jsonify({"response": "success"})
    except Exception as error:
        return jsonify({"error": str(error)}), 400
