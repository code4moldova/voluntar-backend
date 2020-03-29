from flask import Flask
from endpoints import VolunteerAPI, Beneficiary_requestAPI,BeneficiaryAPI,OperatorAPI
from mongoengine import connect
from config import app, SWAGGERUI_BLUEPRINT, SWAGGER_URL, DB_NAME, DB_HOST


app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)

volunteer_view = VolunteerAPI.as_view('volunteers')
app.add_url_rule('/volunteers/list/', defaults={'volunteer_id': None}, view_func=volunteer_view, methods=['GET',])
app.add_url_rule('/volunteers/', view_func=volunteer_view, methods=['POST',])
app.add_url_rule('/volunteers/<volunteer_id>', view_func=volunteer_view, methods=['GET', 'PUT', 'DELETE'])

beneficiary_view = BeneficiaryAPI.as_view('beneficiaries')
app.add_url_rule('/beneficiaries/list/', defaults={'beneficiary_id': None}, view_func=beneficiary_view, methods=['GET',])
app.add_url_rule('/beneficiaries/', view_func=beneficiary_view, methods=['POST',])
app.add_url_rule('/beneficiaries/<beneficiary_id>', view_func=beneficiary_view, methods=['GET', 'PUT', 'DELETE'])

beneficiary_request_view = Beneficiary_requestAPI.as_view('beneficiary_requests')
app.add_url_rule('/beneficiary_requests/list/', defaults={'beneficiary_request_id': None}, view_func=beneficiary_request_view, methods=['GET',])
app.add_url_rule('/beneficiary_requests/', view_func=beneficiary_request_view, methods=['POST',])
app.add_url_rule('/beneficiary_requests/<beneficiary_request_id>', view_func=beneficiary_request_view, methods=['GET', 'PUT', 'DELETE'])

operator_view = OperatorAPI.as_view('operators')
app.add_url_rule('/operators/list/', defaults={'operator_id': None}, view_func=operator_view, methods=['GET',])
app.add_url_rule('/operators/', view_func=operator_view, methods=['POST',])
app.add_url_rule('/operators/<operator_id>', view_func=operator_view, methods=['GET', 'PUT', 'DELETE'])

connect(db=DB_NAME, host=DB_HOST)


@app.route('/')
def hello():
    return ("Hello world")


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)