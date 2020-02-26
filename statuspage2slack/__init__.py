import os

import jinja2
from dotenv import load_dotenv
from flask import Flask

from statuspage2slack.webhook import webhook


class Config(object):

    def __init__(self):
        load_dotenv()

    def __truthy(self, key, default=True):
        if key in os.environ:
            return os.getenv(key).strip().lower() == 'true'
        return default

    @property
    def SLACK_WEBHOOK_URL(self):
        return os.getenv('SLACK_WEBHOOK_URL', None)

    @property
    def COMPONENT_MESSAGES_ENABLED(self):
        return self.__truthy('COMPONENT_MESSAGES_ENABLED')

    @property
    def INCIDENT_MESSAGES_ENABLED(self):
        return self.__truthy('INCIDENT_MESSAGES_ENABLED')

    @property
    def TEMPLATE_FOLDER(self):
        return os.getenv('TEMPLATE_FOLDER', os.getcwd() + '/templates')


def create_app():
    config = Config()
    app = Flask(__name__)

    app.jinja_loader.searchpath.insert(0, config.TEMPLATE_FOLDER)

    app.config.from_object(config)
    app.register_blueprint(webhook)
    return app

