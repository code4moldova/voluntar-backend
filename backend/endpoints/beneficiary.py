from datetime import datetime as dt

from flask.views import MethodView
from flask import jsonify, request, g
from models import Beneficiary,Operator
from config import PassHash, MIN_PASSWORD_LEN
from mongoengine import Q
from endpoints import telegrambot
import logging
log = logging.getLogger("back")

def registerBeneficiary(requestjson, created_by, fixer_id):
        """create a new user"""
        new_beneficiary = requestjson
        if len(created_by)>30:
            user = Operator.verify_auth_token(created_by)
            created_by = user.get().clean_data()['email']
        # TODO: get authenticated Beneficiary and assignee to new Beneficiary
        # new_beneficiary["created_by"] = authenticated_oprator
        try:
            new_beneficiary['password'] = '1112233'
            new_beneficiary['email'] = 'rerre@fdf.ro'
            assert len(new_beneficiary["password"]) >= MIN_PASSWORD_LEN, f"Password is to short, min length is {MIN_PASSWORD_LEN}"
            new_beneficiary["password"] = PassHash.hash(new_beneficiary["password"])
            new_beneficiary['created_by'] = created_by# g.user.get().clean_data()['_id']
            new_beneficiary['fixer'] = str(fixer_id)
            comment = Beneficiary(**new_beneficiary)
            comment.save()
            #telegrambot.send_request(comment)
            return jsonify({"response": "success", 'user': comment.clean_data()})
        except Exception as error:
            return jsonify({"error": str(error)}), 400

def updateBeneficiary(requestjson, beneficiary_id, delete=False):
        """update a single user by id"""
        print(beneficiary_id, '---')
        update = {}
        if not delete:
            for key, value in requestjson.items():
                if key == '_id':
                    continue
                if key == "password":
                    value = PassHash.hash(value)
                update[f"set__{key}"] = value
        else:
            update["set__is_active"] = False

        try:
            obj = Beneficiary.objects(id=beneficiary_id).get()
            data = obj.clean_data()#and not data['is_active']
            if ('set__is_active' in update and update['set__is_active'] and not data['is_active']) \
                or ('set__offer' in update and update['set__offer'] != data['offer']) \
                    or ('set__address' in update and update['set__address'] != data['address']):
                #change to active or different volunteer category or different address
                #return jsonify(telegrambot.send_request(obj))
                telegrambot.send_request(obj)
            elif 'set__volunteer' in update  and ('volunteer' not in data or  update['set__volunteer'] != data['volunteer']):
                telegrambot.send_assign(beneficiary_id, requestjson['volunteer'])
            obj.update(**update)
            return jsonify({"response": "success"})
        except Exception as error:
            return jsonify({"error": str(error)}), 400

def updateBeneficiaryTG(requestjson):
        beneficiary_id = requestjson['request_id']
        print(beneficiary_id, '---')
        update = {
            'questions': 'pretul:'+str(requestjson['amount'])+', simptome:'+','.join(requestjson['symptoms']),
            'comments':requestjson['further_comments'],
            'curator':requestjson['would_return']==1
        }
        
        try:
            obj = Beneficiary.objects(id=beneficiary_id).get()
            data = obj.clean_data()
            obj.update(**update)
            return jsonify({"response": "success"})
        except Exception as error:
            return jsonify({"error": str(error)}), 400

def getBeneficiary(args):
        try:
            id = args.get('id')
            if id:
                beneficiary = Beneficiary.objects(id=id).get().clean_data()
                return jsonify(beneficiary)
            else:
                try:
                    is_active = bool(args.get('is_active', None, bool))
                    first_name = args.get('first_name', None, str)
                    phone = args.get('phone', None, int)
                    created_date_start = args.get('created_date_start', None, dt)
                    created_date_end = args.get('created_date_end', None, dt)
                    item_start = args.get('item_start', None, int)
                    item_end = args.get('item_end', None, int)
                except Exception as _:
                    return jsonify({"error": "Incorrect arg(s)."})

                ben_objs = Beneficiary.objects()
                if(is_active):
                    ben_objs.filter(is_active = is_active)
                if(first_name):
                    ben_objs.filter(first_name=first_name)
                if(phone):
                    ben_objs.filter(phone=phone)
                if(created_date_start and created_date_end):
                    ben_objs.filter((Q(created_at__gte=created_date_start) & Q(created_at__lte=created_date_end)))
                count = ben_objs.all().count()
                if(item_start and item_end):
                    ben_objs.skip(item_start).limit(item_end)
                beneficiaries = [v.clean_data() for v in ben_objs.all()]
                return jsonify({"list": beneficiaries}, {"pagination": {"count_of_records": count}})
        except Exception as error:
            return jsonify({"error": str(error)}), 400


def get_beneficieries_by_filters(filters, pages=0, per_page=10000):
    try:
        item_per_age = int(per_page)
        offset = (int(pages) - 1) * item_per_age
        if len(filters) > 0:
            flt = {}
            toBool = {'true':True, 'false': False}
            caseS = ['first_name', 'last_name']
            for v,k in filters.items():
                flt[v+'__iexact' if v in caseS else v] = toBool[k.lower()] if k.lower() in toBool else k 
            obj = Beneficiary.objects(**flt).order_by('-created_at')
            beneficiaries = [v.clean_data() for v in obj.skip(offset).limit(item_per_age)]
            return jsonify({"list": beneficiaries, 'count':obj.count()})
        else:
            obj = Beneficiary.objects().order_by('-created_at')
            beneficiaries = [v.clean_data() for v in obj.skip(offset).limit(item_per_age)]
            return jsonify({"list": beneficiaries, 'count':obj.count()})
    except Exception as error:
        return jsonify({"error": str(error)}), 400


class BeneficiaryAPI(MethodView):

    def get(self, beneficiary_id:str):
        try:
            if beneficiary_id:
                beneficiary = Beneficiary.objects(id=beneficiary_id).get().clean_data()
                return jsonify(Beneficiary)
            else:
                beneficiaries = [v.clean_data() for v in Beneficiary.objects(is_active=True).all()]
                return jsonify({"list": beneficiaries})
        except Exception as error:
            return jsonify({"error": str(error)}), 400

    def post(self):
        """create a new user"""
        new_Beneficiary = request.json
        # TODO: get authenticated Beneficiary and assignee to new Beneficiary
        # new_Beneficiary["created_by"] = authenticated_oprator
        try:
            assert len(new_Beneficiary["password"]) >= MIN_PASSWORD_LEN, f"Password is to short, min length is {MIN_PASSWORD_LEN}"
            new_Beneficiary["password"] = PassHash.hash(new_Beneficiary["password"])
            comment = Beneficiary(**new_Beneficiary)
            comment.save()
            return jsonify({"response": "success"})
        except Exception as error:
            return jsonify({"error": str(error)}), 400


    def delete(self, beneficiary_id):
        """delete a single user by id"""
        return self.put(beneficiary_id, delete=True)

    def put(self, beneficiary_id, delete=False):
        """update a single user by id"""
        update = {}
        if not delete:
            for key, value in request.json:
                if key == "password":
                    value = PassHash.hash(value)
                update[f"set__{key}"] = value
        else:
            update["set__is_active"] = False

        try:
            Beneficiary.objects(id=beneficiary_id).get().update(**update)
            return jsonify({"response": "success"})
        except Exception as error:
            return jsonify({"error": str(error)}), 400
