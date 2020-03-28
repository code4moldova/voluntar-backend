from flask import Flask
from endpoints import VolunteerAPI
from mongoengine import connect
from config import app, SWAGGERUI_BLUEPRINT, SWAGGER_URL, DB_NAME, DB_HOST


app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)

volunteer_view = VolunteerAPI.as_view('volunteers')
app.add_url_rule('/volunteers/list/', defaults={'volunteer_id': None}, view_func=volunteer_view, methods=['GET',])
app.add_url_rule('/volunteers/', view_func=volunteer_view, methods=['POST',])
app.add_url_rule('/volunteers/<volunteer_id>', view_func=volunteer_view, methods=['GET', 'PUT', 'DELETE'])

connect(db=DB_NAME, host=DB_HOST)


@app.route('/')
def hello():
    return ("Hello world")


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)