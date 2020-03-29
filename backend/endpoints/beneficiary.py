from flask.views import MethodView
from flask import jsonify, request
from models import Beneficiary
from config import PassHash, MIN_PASSWORD_LEN


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
        # TODO: get authenticated operator and assignee to new Beneficiary
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
