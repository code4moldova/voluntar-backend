from flask.views import MethodView
from flask import jsonify, request, g
from models import Volunteer, Beneficiary, Operator
from config import PassHash, MIN_PASSWORD_LEN


def registerVolunteer(requestjson, created_by):
        """create a new user"""
        new_volunteer = requestjson
        if len(created_by)>30:
            user = Operator.verify_auth_token(created_by)
            created_by = user.get().clean_data()['email']
        # TODO: get authenticated operator and assignee to new volunteer
        # new_volunteer["created_by"] = authenticated_oprator
        try:
            assert len(new_volunteer["password"]) >= MIN_PASSWORD_LEN, f"Password is to short, min length is {MIN_PASSWORD_LEN}"
            new_volunteer["password"] = PassHash.hash(new_volunteer["password"])
            assert not Volunteer.objects(email=new_volunteer['email']) , "user with this email already exists"
            new_volunteer['created_by'] = created_by#g.user.get().clean_data()['_id']
            comment = Volunteer(**new_volunteer)
            comment.save()
            return jsonify({"response": "success", 'user': comment.clean_data()})
        except Exception as error:
            return jsonify({"error": str(error)}), 400

def updateVolunteer(requestjson, volunteer_id, delete=False):
        """update a single user by id"""
        print(volunteer_id, '---')
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
            Volunteer.objects(id=volunteer_id).get().update(**update)
            return jsonify({"response": "success"})
        except Exception as error:
            return jsonify({"error": str(error)}), 400

def getVolunteers(filters):
        try:
            if len(filters.getlist('id')) == 1 :
                volunteer_id = filters.get('id')
                volunteer = Volunteer.objects(id=volunteer_id).get().clean_data()
                return jsonify(volunteer)
            elif len(filters.getlist('id')) > 1:
                volunteers = [Volunteer.objects(id=volunteer_id).get().clean_data() for volunteer_id in filters.getlist('id')]
                return jsonify({"list": volunteers})
            else:
                volunteers = [v.clean_data() for v in Volunteer.objects(is_active=True).all()]
                return jsonify({"list": volunteers})
        except Exception as error:
            return jsonify({"error": str(error)}), 400

def getDistance(a, b):
    return (a['longitude']-b['longitude'])**2 + (a['latitude']-b['latitude'])**2
def makejson(v, user):
    u = {'distance':getDistance(v,user), '_id': str(v['_id'])}
    for k in ['first_name','last_name','phone','email','activity_types','availability_day','offer_beneficiary_id']:
        if k in v:
            u[k] =v[k]
    return u
def sort_closest(id, topk):
    topk = int(topk)
    user = Beneficiary.objects(id=id).get().clean_data()
    filters = {}
    #for ac in user['activity_types']:
    #    filters
    #get active volunteer with same activity type, with availability>0 and not bussy with other requests
    volunteers = sorted([makejson(v.clean_data(), user) for v in Volunteer.objects(is_active=True, #availability__gt=0,
                                                                                                     activity_types__in=user['activity_types']).all()\
                            if not Beneficiary.objects(volunteer=str(v.clean_data()['_id']),status__ne='done')
                        ], key=lambda x: x['distance'])
    return jsonify({'list':volunteers[:topk]})


def get_volunteers_by_filters(filters, pages=0, per_page=10000):
    #?availability__gte=4
    try:
        item_per_age = int(per_page)
        offset = (int(pages) - 1) * item_per_age
        if len(filters) > 0:
            obj = Volunteer.objects(**filters)
            volunteers = [v.clean_data() for v in obj.skip(offset).limit(item_per_age)]
            return jsonify({"list": volunteers, 'count':obj.count()})
        else:
            obj = Volunteer.objects(is_active=True)
            volunteers = [v.clean_data() for v in obj.skip(offset).limit(item_per_age)]
            return jsonify({"list": volunteers, 'count':obj.count()})
    except Exception as error:
        return jsonify({"error": str(error)}), 400


def deleteVolunteer(requestjson, volunteer_id):
        updateVolunteer(requestjson, volunteer_id, delete=True)


class VolunteerAPI(MethodView):

    def get(self, volunteer_id:str):
        try:
            if volunteer_id:
                volunteer = Volunteer.objects(id=volunteer_id).get().clean_data()
                return jsonify(volunteer)
            else:
                volunteers = [v.clean_data() for v in Volunteer.objects(is_active=True).all()]
                return jsonify({"list": volunteers})
        except Exception as error:
            return jsonify({"error": str(error)}), 400

    def post(self):
        """create a new user"""
        new_volunteer = request.json
        # TODO: get authenticated operator and assignee to new volunteer
        # new_volunteer["created_by"] = authenticated_oprator
        try:
            assert len(new_volunteer["password"]) >= MIN_PASSWORD_LEN, f"Password is to short, min length is {MIN_PASSWORD_LEN}"
            new_volunteer["password"] = PassHash.hash(new_volunteer["password"])
            comment = Volunteer(**new_volunteer)
            comment.save()
            return jsonify({"response": "success"})
        except Exception as error:
            return jsonify({"error": str(error)}), 400


    def delete(self, volunteer_id):
        """delete a single user by id"""
        return self.put(volunteer_id, delete=True)

    def put(self, volunteer_id, delete=False):
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
            Volunteer.objects(id=volunteer_id).get().update(**update)
            return jsonify({"response": "success"})
        except Exception as error:
            return jsonify({"error": str(error)}), 400
