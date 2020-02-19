import os

from dotenv import dotenv_values
from flask import Flask

from statuspage2slack.webhook import webhook


def create_app():
    app_root = os.path.join(os.path.dirname(__file__), '..')
    dotenv_path = os.path.join(app_root, '.env')

    app = Flask(__name__)
    app.config.from_mapping(dotenv_values(dotenv_path))
    app.register_blueprint(webhook)
    return app
