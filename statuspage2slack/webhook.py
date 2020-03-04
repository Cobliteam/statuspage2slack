import http
import os
from enum import Enum, auto
from shutil import copytree

import click
import requests
from dateutil import parser as datetime_parser
from flask import current_app, request, render_template, Blueprint

webhook = Blueprint('webhook', __name__)


class RequestType(Enum):
    UNKNOWN = auto()
    INCIDENT_UPDATE = auto()
    COMPONENT_UPDATE = auto()


@webhook.cli.command('copy-templates')
@click.argument('folder')
def copy_templates(folder):
    file_path = os.path.realpath(__file__)
    file_folder = os.path.dirname(file_path)
    copytree(file_folder + '/templates', folder)


def discover_request_type(statuspage_data):
    if statuspage_data:
        if 'incident' in statuspage_data:
            return RequestType.INCIDENT_UPDATE
        elif 'component_update' in statuspage_data:
            return RequestType.COMPONENT_UPDATE
    return RequestType.UNKNOWN


def post_message_to_slack(slack_message):
    webhook_url = current_app.config.get('SLACK_WEBHOOK_URL')

    response = requests.post(
        webhook_url, data=slack_message.encode("utf-8"),
        headers={'Content-Type': 'application/json'}
    )
    if response.status_code != 200:
        raise ValueError(
            'Request to slack returned an error %s, the response is:\n%s'
            % (response.status_code, response.text)
        )


@webhook.app_template_filter()
def to_timestamp(date):
    date = datetime_parser.isoparse(date)
    return str(int(date.timestamp()))


@webhook.route('/', methods=['POST'])
def receive_notification():
    statuspage_data = request.get_json()
    request_type = discover_request_type(statuspage_data)
    send_message = False
    if request_type == RequestType.INCIDENT_UPDATE:
        if current_app.config.get('INCIDENT_MESSAGES_ENABLED'):
            slack_message = render_template('incident_update.json',
                                            **statuspage_data)
            send_message = True
    elif request_type == RequestType.COMPONENT_UPDATE:
        if current_app.config.get('COMPONENT_MESSAGES_ENABLED'):
            slack_message = render_template('component_update.json',
                                            **statuspage_data)
            send_message = True
    else:
        return 'Not a valid request', http.HTTPStatus.BAD_REQUEST, {
            'Content-Type': 'text/plain'}

    if send_message:
        post_message_to_slack(slack_message)

    return '', http.HTTPStatus.NO_CONTENT
