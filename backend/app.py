from flask import Flask
from endpoints import VolunteerAPI, Beneficiary_requestAPI,BeneficiaryAPI,OperatorAPI
from mongoengine import connect
from config import app, SWAGGERUI_BLUEPRINT, SWAGGER_URL, DB_NAME, DB_HOST

from endpoints import registerVolunteer, getVolunteers,updateVolunteer, verifyUser, getToken, \
		registerOperator, getOperators, updateOperator
from flask import jsonify, request
from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()

app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)

volunteer_view = VolunteerAPI.as_view('volunteers')
#app.add_url_rule('/volunteers/list/', defaults={'volunteer_id': None}, view_func=volunteer_view, methods=['GET',])
#app.add_url_rule('/volunteers/', view_func=volunteer_view, methods=['POST',])
#app.add_url_rule('/volunteers/<volunteer_id>', view_func=volunteer_view, methods=['GET', 'PUT', 'DELETE'])

connect(db=DB_NAME, host=DB_HOST)

#old school
@auth.verify_password
def verify_password(username, password):
	return verifyUser(username, password)
#volunteers
@app.route('/api/volunteer', methods = ['POST'])
@auth.login_required
def new_user():
	return registerVolunteer(request.json)

@app.route('/api/volunteer', methods = ['GET'])
@auth.login_required
def get_user():
	return getVolunteers(request.args.get('id'))

@app.route('/api/volunteer', methods = ['PUT'])
@auth.login_required
def update_user():
	return updateVolunteer(request.json, request.json['_id'])

@app.route('/api/volunteer', methods = ['DELETE'])
@auth.login_required
def delete_user():
	return updateVolunteer(request.json, request.json['_id'], True)

#operators
@app.route('/api/operator', methods = ['POST'])
#@auth.login_required
def new_operator():
	return registerOperator(request.json)

@app.route('/api/operator', methods = ['GET'])
#@auth.login_required
def get_operator():
	return getOperators(request.args.get('id'))

@app.route('/api/operator', methods = ['PUT'])
@auth.login_required
def update_operator():
	return updateOperator(request.json, request.json['_id'])

@app.route('/api/operator', methods = ['DELETE'])
@auth.login_required
def delete_operator():
	return updateOperator(request.json, request.json['_id'], True)

#authentification
@app.route('/api/token')
@auth.login_required
def get_auth_token():
    token = getToken(auth.username())#g.user.generate_auth_token()
    return jsonify({ 'token': token.decode('ascii') })

#debug part
@app.route('/api/debug', methods = ['GET'])
def get_user3():
	return jsonify(verifyUser('example@mail.com', 'Adm23232in1234'))

@app.route('/')
def hello():
    return ("Hello world")


if __name__ == "__main__":
	#registerOperator({'email':'test@test.com','password':'adminadmin','role':'fixer', 'phone':10000001})#todo: get from enviroment pass
	app.run(host="0.0.0.0", debug=True)