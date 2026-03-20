import os

from flask import Flask, request, Response
from functools import wraps

from backend.app.config import Config
from backend.app.db import close_db, init_db


def _check_basic_auth(username, password):
    return (
        username == Config.API_DOCS_USERNAME
        and password == Config.API_DOCS_PASSWORD
    )


def create_app(testing=False):
    template_dir = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "templates")
    static_dir = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "static")
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    app.config.from_object(Config)

    if testing:
        app.config["TESTING"] = True

    app.teardown_appcontext(close_db)

    with app.app_context():
        init_db(app)
        if not testing:
            from backend.seed import run_seed
            run_seed()

    specs_dir = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "api")
    app.config["SWAGGER"] = {
        "title": "PivdenShop API",
        "uiversion": 3,
        "specs_route": "/api/docs/",
        "openapi": "3.0.3",
    }

    from flasgger import Swagger
    Swagger(app, template_file=os.path.join(specs_dir, "auth.yaml"))

    @app.before_request
    def protect_api_docs():
        if request.path.startswith("/api/docs") or request.path.startswith("/apispec") or request.path.startswith("/flasgger_static"):
            auth = request.authorization
            if not auth or not _check_basic_auth(auth.username, auth.password):
                return Response(
                    "Необхідна автентифікація",
                    401,
                    {"WWW-Authenticate": 'Basic realm="API Docs"'},
                )

    from backend.app.routes.auth import auth_bp
    from backend.app.routes.profile import profile_bp
    from backend.app.routes.products import products_bp
    from backend.app.routes.main import main_bp
    from backend.app.routes.orders import orders_bp
    from backend.app.routes.admin import admin_bp
    from backend.app.routes.cart import cart_bp
    from backend.app.routes.seller import seller_bp
    from backend.app.routes.chats import chats_bp
    from backend.app.routes.notifications import notifications_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(seller_bp)
    app.register_blueprint(chats_bp)
    app.register_blueprint(notifications_bp)

    from backend.app.websocket.chat import init_websocket
    init_websocket(app)

    return app
