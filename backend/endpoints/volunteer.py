from flask.views import MethodView
from flask import jsonify, request, g, make_response
from endpoints.geo import calc_distance

from models import Volunteer, Beneficiary, Operator, Tags
from config import PassHash, MIN_PASSWORD_LEN
from datetime import datetime as dt
from datetime import datetime, timedelta
from datetime import date
import time
import csv
import io
import logging
log = logging.getLogger("back")
from bson import ObjectId
import os
from utils import volunteer_utils as vu


def register_volunteer(request_json, created_by):
    """Creates and persists a new volunteer into database.

    Parameters
    ----------
    request_json : dict
        A dictionary representing the volunteer profile details.
    created_by : str
         A string representing either name of user who is going to create a new volunteer, or the token

    Returns
    -------
    200:
        If the volunteer was successful created and saved.
    400:
        If the volunteer wasn't created or saved, and there was raised some exception.
    """
    log.debug("Relay offer for req:%s from ", request_json) 
    try:
        if not vu.is_email(created_by):
            user = Operator.verify_auth_token(created_by)
            created_by = user.get().clean_data()['email']

        if created_by == os.getenv("COVID_BACKEND_USER"):
            vu.exists_by_telegram_chat_id(request_json["chat_id"])
            new_volunteer_data = process_volunteer_data_from_telegram(request_json)
        else:
            vu.exists_by_email(request_json["email"])
            new_volunteer_data = request_json

        new_volunteer_data["password"] = PassHash.hash(new_volunteer_data["password"])
        new_volunteer_data['created_by'] = created_by
        new_volunteer = Volunteer(**new_volunteer_data)
        new_volunteer.save()
        return jsonify({"response": "success", 'user': new_volunteer.clean_data()})
    except Exception as error:
        return jsonify({"error": str(error)}), 400


def process_volunteer_data_from_telegram(volunteer_data) -> dict:
    """Registers a new volunteer from telegram bot, if no any with given telegram chat ID.

    Parameters
    ----------
    volunteer_data : dict
        A dictionary representing the volunteer profile details.

    Returns
    -------
    dict
        A prepared dictionary to persist into databases.
    """
    volunteer_data["comments"] = ','.join(volunteer_data["activities"])+'; availability:'+str(volunteer_data['availability'])
    volunteer_data.pop("availability")
    volunteer_data.pop("activities")
    volunteer_data["telegram_chat_id"] = str(volunteer_data.pop("chat_id"))
    volunteer_data["telegram_id"] = str(volunteer_data.pop("phoneEx"))
    volunteer_data["password"] = '1111111'
    volunteer_data["address"] = ""  # TODO: Need to discuss what would be persist for new volunteer
    volunteer_data["zone_address"] = ""  # TODO: Need to discuss what would be persist for new volunteer
    volunteer_data["phone"] = vu.convert_phone_to_regional(str(volunteer_data["phone"]))
    volunteer_data["is_active"] = False
    return volunteer_data


def updateVolunteer(requestjson, volunteer_id, delete=False):
        """update a single user by id"""
        print(volunteer_id, '---')
        update = {}
        if not delete:
            for key, value in requestjson.items():
                if key == '_id':
                    continue
                if key == "telegram_id":
                    value = value.replace('+','').replace(' ','').strip()
                    if len(value)==0:
                        update['unset__telegram_chat_id'] = ''
                if key == "password":
                    value = PassHash.hash(value)
                update[f"set__{key}"] = value
        else:
            update["set__is_active"] = False

        try:
            Volunteer.objects(id=volunteer_id).get().update(**update)
            return jsonify({"response": "success"})
        except Exception as error:
            return jsonify({"error": str(error)}), 400

def updateVolunteerTG(requestjson, tg_id, phone):
    update1 = {}
    print(requestjson)
    log.debug("Relay offer for req:%s from ", requestjson)
    for key, value in requestjson.items():
        if key == 'phone':
            continue
        if key == 'telegram_chat_id' and 'phone' not in requestjson:
            continue
        update1[f"set__{key}"] = value
    try:
        if 'phone' in requestjson:#conection between tg and platofrm
            obj = Volunteer.objects(telegram_id=str(requestjson['phone']).replace('+','')).first()
            update = {'set__telegram_chat_id':str(requestjson['telegram_chat_id'])}
        else:
            #get offer from the volunteer
            obj = Volunteer.objects(telegram_chat_id=str(requestjson['telegram_chat_id']), is_active=True).first()
            data = obj.clean_data()
            item = {'id':requestjson['offer_beneficiary_id'], 'offer':requestjson['availability_day']}
            update={'offer_list':data['offer_list']+[item]}
        if obj:
            #obj = [i for i in obj.all()][0]
            obj.update(**update)
        else:
            jsonify({"response": "not found"})
        return jsonify({"response": "success",'l':update,'k':requestjson,'u':update1})
    except Exception as error:
        return jsonify({"error": str(error)}), 400


def update_volunteer(volunteer_id, updates):
    """Updates a volunteer by ID.

    Parameters
    ----------
    volunteer_id : str
        A string representing volunteer ID.
    updates : dict
        A dictionary including name of fields as key and their values for updating.
    """
    try:
        Volunteer.objects(id=volunteer_id).get().update(**updates)
    except Exception as error:
        log.error("An error occurred on updating Volunteers. {}".format(error.message))


def getVolunteers(filters):
        try:
            if len(filters.getlist('id')) == 1 :
                volunteer_id = filters.get('id')
                volunteer = Volunteer.objects(id=volunteer_id).get().clean_data()

                return jsonify(volunteer)
            elif len(filters.getlist("telegram_chat_id")) == 1:
                telegram_id = filters.get("telegram_chat_id")
                if len(Volunteer.objects(telegram_chat_id=telegram_id)) == 0:
                    return jsonify({"exists": False})
                else:
                    return jsonify({"exists": True})
            elif len(filters.getlist('id')) > 1:
                volunteers = [Volunteer.objects(id=volunteer_id).get().clean_data() for volunteer_id in filters.getlist('id')]
                return jsonify({"list": volunteers})
            else:
                volunteers = [v.clean_data() for v in Volunteer.objects(is_active=True).order_by('-created_at').all()]
                for i,volunteer in enumerate(volunteers):
                    volunteers[i]['cases_solved'] =  Beneficiary.objects(volunteer=volunteer['_id']).count()
                return jsonify({"list": volunteers})
        except Exception as error:
            return jsonify({"error": str(error)}), 400


def utc_short_to_user_short(short_time):
    """Transform a short '%H:%M' time notation from UTC to the user's timezone
    :params short_time: str, timestamp in %H:%M format
    :returns: str, timestamp in the same format, but adapted to the user's timezone"""
    raw = datetime.strptime(short_time, "%H:%M")
    localized = raw + timedelta(hours=3)
    return localized.strftime("%H:%M")

def makejson(v, user):
    u = {'distance': calc_distance(v, user), '_id': str(v['_id'])}
    for k in ['first_name','last_name','phone','email','activity_types', 'telegram_chat_id', 'latitude','longitude']:
        if k in v:
            u[k] =v[k]
    u['accepted_offer'] = False
    for it in v['offer_list']:
        if it['id'] == user['_id']:
            u['availability_day'] = utc_short_to_user_short(it['offer'])
            u['accepted_offer'] = True
    u['count'] = Beneficiary.objects(volunteer=str(v['_id']),created_at__lte=dt.now() - timedelta(days=1)).count()
    return u
def sort_closest(id, topk, category):
    topk = int(topk)
    user = Beneficiary.objects(id=id).get().clean_data()
    filters = {}
    #get active volunteer with same activity type, with availability>0 and not bussy with other requests
    if 'offer' in user and user['offer']!='':
        category = user['offer']
        volunteers = sorted([makejson(v.clean_data(), user) for v in Volunteer.objects(is_active=True, #availability__gt=0,
                                                                                                         offer=category).all()\
                               # if not Beneficiary.objects(volunteer=str(v.clean_data()['_id']),status__ne='done')
                                ], key=lambda x: x['distance'])
    else:
        volunteers = sorted([makejson(v.clean_data(), user) for v in Volunteer.objects(is_active=True, #availability__gt=0,
                                                                                                         activity_types__in=user['activity_types']).all()\
                            ], key=lambda x: x['distance'])
    volunteers = [i for i in volunteers if i['distance']<100000]
    #todo: find the best threshhold!!!

    if 'volunteer' in user and user['volunteer']!='':
        volunteers = [makejson(Volunteer.objects(id=user['volunteer']).get().clean_data(), user)] + [i for i in volunteers if i['_id'] != user['volunteer']]
    return jsonify({'list':volunteers[:topk]})


def get_volunteers_by_filters(filters, pages=0, per_page=10000):
    try:
        item_per_age = int(per_page)
        offset = (int(pages) - 1) * item_per_age
        if len(filters) > 0:
            flt = {}
            toBool = {'true':True, 'false': False}
            caseS = ['first_name', 'last_name']
            for v,k in filters.items():
                flt[v+'__iexact' if v in caseS else v] = toBool[k.lower()] if k.lower() in toBool else k

            obj = Volunteer.objects(**flt)
            volunteers = [v.clean_data() for v in obj.order_by('-created_at').skip(offset).limit(item_per_age)]
            for i,volunteer in enumerate(volunteers):
                    volunteers[i]['cases_solved'] =  Beneficiary.objects(volunteer=volunteer['_id']).count()
            return jsonify({"list": volunteers, 'count':obj.count()})
        else:
            obj = Volunteer.objects().order_by('-created_at')
            volunteers = [v.clean_data() for v in obj.skip(offset).limit(item_per_age)]
            for i,volunteer in enumerate(volunteers):
                    volunteers[i]['cases_solved'] =  Beneficiary.objects(volunteer=volunteer['_id']).count()
            return jsonify({"list": volunteers, 'count':obj.count()})
    except Exception as error:
        return jsonify({"error": str(error)}), 400


def deleteVolunteer(requestjson, volunteer_id):
        updateVolunteer(requestjson, volunteer_id, delete=True)

def boolconv(source, k, tag2v):
    if k in tag2v:
        if ObjectId.is_valid(source):
            tg = Tags.objects(id=source)#
        
            if tg:
                return tg.get().clean_data()['ro']
    if source is None:
        return '0'
    if type(source) is str:
        if len(source)==0:
            return '0'
        else:
            return source
    if type(source) is bool:
        if source:
            return 1
        else:
            return 0
    else:
        return str(source)

def volunteer_build_csv():
    includelist = ['first_name', 'last_name', 'phone' ,  'address', 'zone_address', 'age', 
                   'offer', 'comments',  'urgent','curator','has_disabilities','black_list', 'received_contract']

    tag2v = {'offer':'offer', 'age':'age', 'zone_address':'sector'}

    si = io.StringIO()
    writer = csv.writer(si)
    volunteers = [v.include_data(includelist) for v in Volunteer.objects().all()]

    # write header
    writer.writerow(includelist)

    # write data
    for doc in volunteers:
        writer.writerow([boolconv(doc[k], k, tag2v) for k in doc])

    output = make_response(si.getvalue())
    output.headers["Content-type"] = "text/csv"
    output.headers["Content-Disposition"] = "attachment; filename=volunteer.csv"
    return output

