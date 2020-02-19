import pytest
import responses
from flask import Flask, template_rendered
from flask.testing import FlaskClient

from statuspage2slack import create_app


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
def request_mocker():
    with responses.RequestsMock(
            assert_all_requests_are_fired=False) as req_mocker:
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
