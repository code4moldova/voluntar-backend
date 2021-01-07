from flask import jsonify, request
from flask_cors import CORS
from flask_httpauth import HTTPBasicAuth
from mongoengine import connect

from config import DB_HOST, DB_NAME, SWAGGER_URL, SWAGGERUI_BLUEPRINT
from endpoints import (
    get_beneficiaries_by_filters,
    get_operators_by_filters,
    get_volunteers_by_filters,
    getBeneficiary,
    getOperators,
    getVolunteers,
    parseFile,
    register_volunteer,
    registerBeneficiary,
    registerOperator,
    updateBeneficiary,
    updateOperator,
    updateVolunteer,
    verifyUser,
    create_request,
    getTags,
    registerTag,
    register_notification,
    get_notifications_by_filters,
    register_cluster,
)
from endpoints.requests import get_requests_by_id
from endpoints.requests import update_request, update_request_status
from endpoints.volunteer import volunteer_build_csv
from server import create_application

auth = HTTPBasicAuth()

app = create_application(auth)
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)

cors = CORS(app)

connect(db=DB_NAME, host=DB_HOST)


@app.route("/auto-reload-test")
def auto_reload_test():
    return "auto_reload_test"


# volunteers
@app.route("/api/volunteer", methods=["POST"])
@auth.login_required
def new_user():
    return register_volunteer(request.json, auth.username())


@app.route("/api/volunteer", methods=["GET"])
@auth.login_required
def get_user():
    return getVolunteers(request.args)  # request.args.get('id'))


@app.route("/api/volunteer/filters", methods=["GET"])
@app.route("/api/volunteer/filters/<pages>/<per_page>", methods=["GET"])
@auth.login_required
def get_user_by_filters(pages=15, per_page=10):
    return get_volunteers_by_filters(request.args, pages, per_page)


@app.route("/api/volunteer", methods=["PUT"])
@auth.login_required
def update_user():
    return updateVolunteer(request.json, request.json["_id"])


@app.route("/api/volunteer", methods=["DELETE"])
@auth.login_required
def delete_user():
    return updateVolunteer(request.json, request.json["_id"], True)


@app.route("/api/volunteer/parse/", methods=["GET"])
@auth.login_required
def parse_user():
    url = request.args.get("url")
    b = request.args.get("b")
    e = request.args.get("e")
    return parseFile(url, b, e, request.args)


@app.route("/api/export/csv/volunteers", methods=["GET"])
@auth.login_required
def build_csv():
    try:
        return volunteer_build_csv()
    except Exception as error:
        return jsonify({"error": str(error)}), 400


# operators
@app.route("/api/operator", methods=["POST"])
@auth.login_required
def new_operator():
    return registerOperator(request.json, auth.username())


@app.route("/api/operator", methods=["GET"])
@auth.login_required
def get_operator():
    return getOperators(request.args.get("id"))


@app.route("/api/operator", methods=["PUT"])
@auth.login_required
def update_operator():
    return updateOperator(request.json, request.json["_id"])


@app.route("/api/operator", methods=["DELETE"])
@auth.login_required
def delete_operator():
    return updateOperator(request.json, request.json["_id"], True)


@app.route("/api/operator/filters", methods=["GET"])
@app.route("/api/operator/filters/<pages>/<per_page>", methods=["GET"])
@auth.login_required
def get_operator_by_filters(pages=15, per_page=10):
    return get_operators_by_filters(request.args, pages, per_page)


# tag
@app.route("/api/tag", methods=["GET"])
@app.route("/api/tag/<select>", methods=["GET"])
@auth.login_required
def get_tag(select="all"):
    return getTags(request.args.get("id"), select)


@app.route("/api/tag", methods=["POST"])
@auth.login_required
def newregisterTag():
    return registerTag(request.json, auth.username())


# beneficiari
@app.route("/api/beneficiary", methods=["POST"])
@auth.login_required
def new_beneficiary():
    return registerBeneficiary(request.json, auth.username())


@app.route("/api/beneficiary", methods=["GET"])
@auth.login_required
def get_beneficiary():
    return getBeneficiary(request.args)


@app.route("/api/beneficiary", methods=["PUT"])
@auth.login_required
def update_beneficiary():
    return updateBeneficiary(request.json, request.json["_id"])


@app.route("/api/beneficiary/filters", methods=["GET"])
@app.route("/api/beneficiary/filters/<pages>/<per_page>", methods=["GET"])
@auth.login_required
def get_beneficiary_by_filters(pages=15, per_page=10):
    return get_beneficiaries_by_filters(request.args, pages, per_page)


@app.route("/api/requests", methods=["PUT"])
@auth.login_required
def put_requests():
    return update_request(request.json["_id"], request.json)


@app.route("/api/requests/update", methods=["PUT"])
def put_status_requests():
    return update_request_status(request.json["_id"], request.json["cluster_id"], request.json)


@app.route("/api/requests/<request_id>", methods=["GET"])
@auth.login_required
def get_requests(request_id):
    return get_requests_by_id(request_id)


# user request
@app.route("/api/requests", methods=["POST"])
@auth.login_required
def new_user_request():
    return create_request(request.json, auth.username())


# notifications
@app.route("/api/notifications", methods=["POST"])
@auth.login_required
def new_notification():
    return register_notification(request.json)


@app.route("/api/notifications/filters", methods=["GET"])
@app.route("/api/notifications/filters/<pages>/<per_page>", methods=["GET"])
@auth.login_required
def get_notification_by_filters(pages=1, per_page=10):
    return get_notifications_by_filters(request.args, pages, per_page)


# clusters
@app.route("/api/clusters", methods=["POST"])
@auth.login_required
def new_cluster():
    return register_cluster(request.json)


# debug part
@app.route("/api/debug", methods=["GET"])
def get_user3():
    return jsonify(verifyUser("example@mail.com", "Adm23232in1234"))


@app.route("/")
def hello():
    return "It Works."


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
