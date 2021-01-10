import io
import csv

from flask import make_response

from services.table_list import service


def register(app, auth):
    @app.route("/api/export/csv/<slug>", methods=["GET"])
    @auth.login_required
    def export_csv(slug):
        rows = service(slug)
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerows(rows)
        output = make_response(buffer.getvalue())
        output.headers["Content-type"] = "text/csv"
        output.headers["Content-Disposition"] = "attachment; filename={}.csv".format(slug)
        return output
