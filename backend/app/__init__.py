from flask import Flask

from backend.app.config import Config
from backend.app.db import close_db, init_db


def create_app(testing=False):
    import os
    template_dir = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "templates")
    static_dir = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "static")
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    app.config.from_object(Config)

    if testing:
        app.config["TESTING"] = True

    app.teardown_appcontext(close_db)

    with app.app_context():
        init_db(app)

    from backend.app.routes.auth import auth_bp
    from backend.app.routes.profile import profile_bp
    from backend.app.routes.products import products_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(products_bp)

    return app
