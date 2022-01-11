from flask import Flask, request
from mongoengine import connect

from dub.views.urls import blueprint


def init_auth(app):
    @app.before_request
    def before_request():
        headers = request.headers
        if (
            "Authorization" in headers
            and headers["Authorization"] == f'Bearer {app.config["AUTH_TOKEN"]}'
            or request.endpoint is None
            or request.endpoint in ["api.home"]
        ):
            return

        return "", 403    

def create_app(config_filename):
    """Application factory."""
    app = Flask(__name__)
    app.config.from_object(config_filename)
    app.app_context().push()
    
    # Connect to mongo
    connect(host=app.config["DB_URL"])

    # # Create media root
    # os.mkdir(app.config['MEDIA_ROOT'])

    app.register_blueprint(blueprint)

    init_auth(app)

    return app