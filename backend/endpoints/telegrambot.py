import requests
from .volunteer import sort_closest
from config import AJUBOT_HOST, AJUBOT_PORT

BASE_URL = f'{AJUBOT_HOST}:{AJUBOT_PORT}'


def send_request(beneficiary):
    beneficiary_id = str(beneficiary['id'])
    payload = {
        'request_id': beneficiary_id,
        'beneficiary': beneficiary.first_name + ' ' + beneficiary.last_name,
        'address': beneficiary.address,
        'needs': beneficiary.activity_types,
        'gotSymptoms': beneficiary.has_symptoms,
        'safetyCode': beneficiary.secret,
        'phoneNumber': beneficiary.phone,
        'remarks': beneficiary.remarks,
        'volunteers': [v['telegram_chat_id'] for v in sort_closest(beneficiary_id, 5).json['list']]
    }
    requests.post(f'{BASE_URL}/help_request', json=payload)
