import io
import csv
import json
from flask import jsonify, request
from flask import make_response

from bson import ObjectId

from models import Beneficiary, Volunteer, Request, User, Operator
from utils import volunteer_utils as vu


def clean_phone(text, max_length=8):
    digits = [i for i in text if i.isnumeric()]
    return "".join(digits[-max_length:])


def clean_json(data, fields, f):
    for k in fields:
        if k in data:
            data[k] = f(data[k])
    return data


class ImportRequests:
    FIELDS = "last_name first_name age phone zone address apartment entrance floor special_condition latitude longitude".split()
    FIELDS_FLOAT = "latitude longitude".split()
    FIELDS_INT = "age".split()
    FIELDS_REQUIRED = "last_name first_name age phone address zone".split()

    def run(self, data, created_by):

        try:
            if not vu.is_email(created_by):
                user = Operator.verify_auth_token(created_by)
                created_by = user.get().clean_data()["email"]
            created = []
            for i, item in enumerate(data):

                new_beneficiary_data = {k: item[k] for k in self.FIELDS if (k in item and len(item[k].strip()) > 0)}

                for k in self.FIELDS_REQUIRED:
                    if k not in new_beneficiary_data:
                        return jsonify({"error": "field {} is required".format(k), "d": new_beneficiary_data}), 400

                clean_json(new_beneficiary_data, self.FIELDS_FLOAT, float)
                clean_json(new_beneficiary_data, self.FIELDS_INT, int)
                clean_json(new_beneficiary_data, ["phone", "landline"], clean_phone)

                old_beneficiary = Beneficiary.objects(phone=new_beneficiary_data["phone"])
                if old_beneficiary:
                    new_beneficiary = old_beneficiary.get()
                else:
                    new_beneficiary_data["created_by"] = created_by
                    new_beneficiary = Beneficiary(**new_beneficiary_data)
                    new_beneficiary.save()
                    created.append(new_beneficiary.clean_data())

                user = User.objects(email=created_by).get()
                new_request_data = dict(status="new", type="medicine", beneficiary=new_beneficiary, user=user)
                new_request = Request(**new_request_data)
                new_request.save()
                created.append(new_request.clean_data())

            return jsonify({"response": "success", "data": created})
        except Exception as error:
            return jsonify({"error": str(error)}), 400


class ImportVolunteers:
    FIELDS = "last_name first_name age phone zone address email facebook_profile role availability_hours_start availability_hours_end availability_days".split()
    FIELDS_LIST = "role availability_days".split()
    FIELDS_INT = "availability_hours_end age availability_hours_start".split()
    FIELDS_REQUIRED = "last_name first_name age phone zone".split()

    def run(self, data, created_by):

        try:
            if not vu.is_email(created_by):
                user = Operator.verify_auth_token(created_by)
                created_by = user.get().clean_data()["email"]
            created = []
            for i, item in enumerate(data):

                new_volunteer_data = {k: item[k] for k in self.FIELDS if (k in item and len(item[k].strip()) > 0)}

                for k in self.FIELDS_REQUIRED:
                    if k not in new_volunteer_data:
                        return jsonify({"error": "field {} is required".format(k), "d": new_volunteer_data}), 400

                clean_json(new_volunteer_data, self.FIELDS_INT, int)

                # todo: load the list from csv
                new_volunteer_data["role"] = ["delivery"]
                new_volunteer_data["availability_days"] = ["saturday"]
                # clean_json(new_volunteer_data, self.FIELDS_LIST, json.loads)

                clean_json(new_volunteer_data, ["phone", "landline"], clean_phone)
                if Volunteer.objects(phone=new_volunteer_data["phone"]) or Volunteer.objects(
                    email=new_volunteer_data["email"]
                ):
                    created.append(dict(exists=new_volunteer_data["phone"]))
                    continue

                new_volunteer_data["created_by"] = created_by
                new_volunteer = Volunteer(**new_volunteer_data)
                new_volunteer.save()
                created.append(new_volunteer.clean_data())

            return jsonify({"response": "success", "data": created})
        except Exception as error:
            return jsonify({"error": str(error)}), 400


SERVICES = {
    "volunteers": ImportVolunteers,
    "requests": ImportRequests,
}


def register(app, auth):
    @app.route("/api/import/csv/<slug>", methods=["POST"])
    @auth.login_required
    def import_from_csv(slug):
        if slug not in SERVICES:
            return jsonify({"error": "Url is not valid"}), 400
        if "file" not in request.files:
            return jsonify({"error": "No file"}), 400
        f = request.files["file"]
        if not f:
            return jsonify({"error": "No file"}), 400

        stream = io.StringIO(f.stream.read().decode("UTF8"), newline=None)
        csv_input = csv.reader(stream)
        data = []
        header = None
        for row in csv_input:
            if header is None:
                header = row
                continue
            data.append({k: row[i] for i, k in enumerate(header)})

        return SERVICES[slug]().run(data, auth.username())
