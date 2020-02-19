import os

import requests
from flask import Flask, request, render_template, jsonify

app = Flask(__name__)


@app.route('/', methods=['POST'])
def receive_notification():
    statuspage_data = request.get_json()
    slack_message = render_template('component_update.json', **statuspage_data)
    post_message_to_slack(slack_message)
    return jsonify(slack_message)


def post_message_to_slack(slack_message):
    webhook_url = os.getenv('SLACK_WEBHOOK_URL')

    response = requests.post(
        webhook_url, data=slack_message,
        headers={'Content-Type': 'application/json'}
    )
    if response.status_code != 200:
        raise ValueError(
            'Request to slack returned an error %s, the response is:\n%s'
            % (response.status_code, response.text)
        )