from flask.views import MethodView
from flask import jsonify, request
from models import Beneficiary
from config import PassHash, MIN_PASSWORD_LEN


class BeneficiaryAPI(MethodView):

    def get(self, Beneficiary_id:str):
        try:
            if Beneficiary_id:
                Beneficiary = Beneficiary.objects(id=Beneficiary_id).get().clean_data()
                return jsonify(Beneficiary)
            else:
                Beneficiarys = [v.clean_data() for v in Beneficiary.objects(status='new').all()]
                return jsonify({"list": Beneficiarys})
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


    def delete(self, Beneficiary_id):
        """delete a single user by id"""
        return self.put(Beneficiary_id, delete=True)

    def put(self, Beneficiary_id, delete=False):
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
            Beneficiary.objects(id=Beneficiary_id).get().update(**update)
            return jsonify({"response": "success"})
        except Exception as error:
            return jsonify({"error": str(error)}), 400
