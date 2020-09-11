def register(app):
    @app.route("/welcome")
    def welcome():
        return "Hello, World!"
