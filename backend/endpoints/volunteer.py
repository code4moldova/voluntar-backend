from flask.views import MethodView
from flask import jsonify, request
from models import Volunteer
from config import PassHash, MIN_PASSWORD_LEN


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
