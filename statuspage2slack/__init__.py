from dotenv import dotenv_values
from flask import Flask

from statuspage2slack.webhook import webhook


class Config(object):

    def __init__(self):
        self.env_values = dotenv_values()

    def __truthy(self, key, default=True):
        if key in self.env_values:
            return self.env_values[key].strip().lower() == 'true'
        return default

    @property
    def SLACK_WEBHOOK_URL(self):
        return self.env_values.get('SLACK_WEBHOOK_URL', None)

    @property
    def COMPONENT_MESSAGES_ENABLED(self):
        return self.__truthy('COMPONENT_MESSAGES_ENABLED')

    @property
    def INCIDENT_MESSAGES_ENABLED(self):
        return self.__truthy('INCIDENT_MESSAGES_ENABLED')


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config())
    app.register_blueprint(webhook)
    return app
