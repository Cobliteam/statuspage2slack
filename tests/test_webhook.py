import json
import os

import pytest
import responses
from faker import Faker
from flask import template_rendered, Response
from flask.testing import FlaskClient
from requests import PreparedRequest

from statuspage2slack import webhook
from statuspage2slack.statuspage_constants import ComponentStatus

fake = Faker()

STATUSPAGE_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%SZ'


@pytest.fixture
def component_update_request(old_component_status, new_component_status):
    creation_datetime = fake.past_datetime()
    update_datetime = fake.past_datetime(start_date=creation_datetime)
    component_id = fake.bothify(text='????????????')
    update_id = fake.bothify(text='????????????')
    return {
        "component_update": {
            "created_at": update_datetime.strftime(STATUSPAGE_DATETIME_FORMAT),
            "new_status": new_component_status.value,
            "old_status": old_component_status.value,
            "id": update_id,
            "component_id": component_id
        },
        "component": {
            "created_at": creation_datetime.strftime(
                STATUSPAGE_DATETIME_FORMAT),
            "id": component_id,
            "name": "Some Component",
            "status": new_component_status.value
        }
    }


@pytest.fixture
def client() -> FlaskClient:
    webhook.app.config['TESTING'] = True
    with webhook.app.test_client() as client:
        yield client


@pytest.fixture
def request_mocker():
    with responses.RequestsMock(
            assert_all_requests_are_fired=False) as req_mocker:
        yield req_mocker


@pytest.fixture()
def used_templates():
    recorded = []

    def record(_, template, context):
        recorded.append((template, context))

    template_rendered.connect(record, webhook.app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, webhook.app)


def is_json(some_string):
    try:
        json.loads(some_string)
    except ValueError:
        return False
    return True


@pytest.mark.parametrize("old_component_status", ComponentStatus)
@pytest.mark.parametrize("new_component_status", ComponentStatus)
def test_component_update(client: FlaskClient, component_update_request,
                          used_templates,
                          request_mocker: responses.RequestsMock):
    def assert_request(request: PreparedRequest):
        assert request.body
        assert is_json(request.body)

        return 200, {}, 'ok'

    request_mocker.add_callback(responses.POST, os.getenv('SLACK_WEBHOOK_URL'),
                                callback=assert_request)

    response: Response = client.post('/', json=component_update_request)

    assert 200 <= response.status_code < 300

    assert len(used_templates) == 1
    (template, context) = used_templates.pop()
    assert template.name == 'component_update.json'
    assert context['component_update'] == \
           component_update_request['component_update']
    assert context['component'] == component_update_request['component']
