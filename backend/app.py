from flask import Flask
from endpoints import  telegrambot
from endpoints.volunteer import volunteer_build_csv
from mongoengine import connect
from config import SWAGGERUI_BLUEPRINT, SWAGGER_URL, DB_NAME, DB_HOST
from server import create_application
from endpoints import register_volunteer, getVolunteers,updateVolunteer, verifyUser, getToken, \
		registerOperator, getOperators, updateOperator, \
		registerBeneficiary, getBeneficiary, updateBeneficiary, get_volunteers_by_filters, get_active_operator, get_beneficiaries_by_filters, \
		get_operators_by_filters, sort_closest, registerTag, getTags, updateTag, parseFile, updateVolunteerTG, updateBeneficiaryTG
from flask import jsonify, request
from flask_httpauth import HTTPBasicAuth
from flask_cors import CORS
import os, json, random
auth = HTTPBasicAuth()

app = create_application()
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)

cors = CORS(app)

connect(db=DB_NAME, host=DB_HOST)

#old school
@auth.verify_password
def verify_password(username, password):
	return verifyUser(username, password)

#volunteers
@app.route('/api/volunteer', methods = ['POST'])
@auth.login_required
def new_user():
	return register_volunteer(request.json, auth.username())

@app.route('/api/volunteer', methods = ['GET'])
@auth.login_required
def get_user():
	return getVolunteers(request.args)#request.args.get('id'))


@app.route('/api/volunteer/filters', methods=['GET'])
@app.route('/api/volunteer/filters/<pages>/<per_page>', methods=['GET'])
@auth.login_required
def get_user_by_filters(pages=15, per_page=10):
	return get_volunteers_by_filters(request.args, pages, per_page)


@app.route('/api/volunteer', methods = ['PUT'])
@auth.login_required
def update_user():
	if '_id' not in request.json:
		return updateVolunteerTG(request.json, request.json.get('telegram_chat_id'), request.json.get('phone'))
	else:
		return updateVolunteer(request.json, request.json['_id'])


@app.route('/api/volunteer/closest', methods=['GET', 'POST'])
@app.route('/api/volunteer/closest/<id>/<topk>', methods=['GET', "POST"])
@auth.login_required
def get_closest_user(id, topk):
	return sort_closest(id, topk, request.args.get('category'))

@app.route('/api/volunteer', methods = ['DELETE'])
@auth.login_required
def delete_user():
	return updateVolunteer(request.json, request.json['_id'], True)


@app.route('/api/volunteer/parse/', methods = ['GET'])
@auth.login_required
def parse_user():
	url = request.args.get('url')
	b = request.args.get('b')
	e = request.args.get('e')
	return parseFile(url, b, e, request.args)

@app.route('/api/export/csv/volunteers', methods = ['GET'])
@auth.login_required
def build_csv():
	try:
		return volunteer_build_csv()
	except Exception as error:
		return jsonify({"error": str(error)}), 400

	return jsonify({"response": "success"})

#tags

@app.route('/api/tag', methods = ['POST'])
@auth.login_required
def new_tag():
	return registerTag(request.json, auth.username())

@app.route('/api/tag', methods = ['GET'])
@app.route('/api/tag/<select>', methods=['GET'])
@auth.login_required
def get_tag(select='all'):
	return getTags(request.args.get('id'), select)

@app.route('/api/tag', methods = ['PUT'])
@auth.login_required
def update_tag():
	return updateTag(request.json, request.json['_id'])

@app.route('/api/tagedit', methods = ['GET',"POST"])
@auth.login_required
def update_tag_get():
	if request.method == 'POST':
		js = json.loads(request.form.get('json'))
		for it in js:
			it['is_active'] = 'true' if it['is_active'] else 'false'
			updateTag({k:v for k,v in it.items() if k is  not '_id'}, it['_id'])
		return jsonify(js)
	tg = getTags(False, request.args.get('name'), False)
	dd = []
	return '<form action="" method="post" ><textarea style="    width: 800px;  height: 400px;" name="json">'+json.dumps(tg, indent=4, sort_keys=True)+'</textarea><button>go</button></form>'
	return updateTag(request.args, request.args.get('_id'))

@app.route('/api/tag', methods = ['DELETE'])
@auth.login_required
def delete_tag():
	return updateTag(request.json, request.json['_id'], True)


# operators
@app.route('/api/operator', methods = ['POST'])
@auth.login_required
def new_operator():
	return registerOperator(request.json, auth.username())


@app.route('/api/operator', methods = ['GET'])
@auth.login_required
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

@app.route('/api/operator/filters', methods=['GET'])
@app.route('/api/operator/filters/<pages>/<per_page>', methods=['GET'])
@auth.login_required
def get_operator_by_filters(pages=15, per_page=10):
	return get_operators_by_filters(request.args, pages, per_page)


#beneficiari
@app.route('/api/beneficiary', methods = ['POST'])
@auth.login_required
def new_beneficiary():
    fixer_id = get_active_operator()
    return registerBeneficiary(request.json, auth.username(), fixer_id)

@app.route('/api/beneficiary', methods = ['GET'])
@auth.login_required
def get_beneficiary():
	return getBeneficiary(request.args)


@app.route('/api/secret', methods = ['GET'])
@auth.login_required
def get_secret():
	return jsonify({'secret' : random.choice('abcdefghijklmnopqrstuvwxyz').upper()+ str(random.choice(range(1000)))})


@app.route('/api/beneficiary', methods = ['PUT'])
@auth.login_required
def update_beneficiary():
	if 'wellbeing' in request.json:
		return updateBeneficiaryTG(request.json)
	return updateBeneficiary(request.json, request.json['_id'])


@app.route('/api/beneficiary/filters', methods=['GET'])
@app.route('/api/beneficiary/filters/<pages>/<per_page>', methods=['GET'])
@auth.login_required
def get_beneficiary_by_filters(pages=15, per_page=10):
	return get_beneficiaries_by_filters(request.args, pages, per_page)

#debug part
@app.route('/api/debug', methods = ['GET'])
def get_user3():
	return jsonify(verifyUser('example@mail.com', 'Adm23232in1234'))


@app.route('/')
def hello():
	return "It Works."


@app.route('/api/receipt', methods=['POST'])
def upload_image():
	return telegrambot.save_receive(request.json['beneficiary_id'], request.json['data'])


if __name__ == "__main__":
	app.run(host="0.0.0.0", debug=True)
