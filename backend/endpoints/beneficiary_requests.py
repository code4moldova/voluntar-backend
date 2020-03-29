from flask.views import MethodView
from flask import jsonify, request
from models import Beneficiary_request
from config import PassHash, MIN_PASSWORD_LEN


class Beneficiary_requestAPI(MethodView):

    def get(self, Beneficiary_request_id:str):
        try:
            if Beneficiary_request_id:
                Beneficiary_request = Beneficiary_request.objects(id=Beneficiary_request_id).get().clean_data()
                return jsonify(Beneficiary_request)
            else:
                Beneficiary_requests = [v.clean_data() for v in Beneficiary_request.objects(is_active=True).all()]
                return jsonify({"list": Beneficiary_requests})
        except Exception as error:
            return jsonify({"error": str(error)}), 400

    def post(self):
        """create a new user"""
        new_Beneficiary_request = request.json
        # TODO: get authenticated operator and assignee to new Beneficiary_request
        # new_Beneficiary_request["created_by"] = authenticated_oprator
        try:
            assert len(new_Beneficiary_request["password"]) >= MIN_PASSWORD_LEN, f"Password is to short, min length is {MIN_PASSWORD_LEN}"
            new_Beneficiary_request["password"] = PassHash.hash(new_Beneficiary_request["password"])
            comment = Beneficiary_request(**new_Beneficiary_request)
            comment.save()
            return jsonify({"response": "success"})
        except Exception as error:
            return jsonify({"error": str(error)}), 400


    def delete(self, Beneficiary_request_id):
        """delete a single user by id"""
        return self.put(Beneficiary_request_id, delete=True)

    def put(self, Beneficiary_request_id, delete=False):
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
            Beneficiary_request.objects(id=Beneficiary_request_id).get().update(**update)
            return jsonify({"response": "success"})
        except Exception as error:
            return jsonify({"error": str(error)}), 400
