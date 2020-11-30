import csv

from flask import make_response


def register(app, auth):
    @app.route("/api/import/csv/<slug>", methods=["PUT"])
    @auth.login_required
    def import_csv(slug):
        reader = csv.reader(slug)
        input_csv = make_response(reader.getvalue())
        return input_csv
