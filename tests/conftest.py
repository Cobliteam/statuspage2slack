import json

import pytest
import responses
from flask import Flask, template_rendered
from flask.testing import FlaskClient
from requests import PreparedRequest

from statuspage2slack import create_app


@pytest.fixture
def change_env(monkeypatch, env_dict: dict):
    for key, value in env_dict.items():
        monkeypatch.setenv(key, value)

@pytest.fixture
def flask_app() -> Flask:
    app = create_app()
    app.config['TESTING'] = True
    return app


@pytest.fixture
def flask_client(flask_app) -> FlaskClient:
    with flask_app.test_client() as client:
        yield client


@pytest.fixture
def request_mocker(flask_app):
    with responses.RequestsMock(
            assert_all_requests_are_fired=False) as req_mocker:
        def assert_request(request: PreparedRequest):
            assert request.body
            assert is_json(request.body)

            return 200, {}, 'ok'

        req_mocker.add_callback(responses.POST,
                                flask_app.config.get('SLACK_WEBHOOK_URL'),
                                callback=assert_request)

        yield req_mocker


@pytest.fixture()
def used_templates(flask_app):
    recorded = []

    def record(_, template, context):
        recorded.append((template, context))

    template_rendered.connect(record, flask_app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, flask_app)


def is_json(some_string):
    try:
        json.loads(some_string)
    except ValueError:
        return False
    return True
