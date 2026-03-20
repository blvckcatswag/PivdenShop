from flask import Flask

from backend.app.config import Config
from backend.app.db import close_db


def create_app(testing=False):
    app = Flask(__name__)
    app.config.from_object(Config)

    if testing:
        app.config["TESTING"] = True

    app.teardown_appcontext(close_db)

    from backend.app.routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    return app
