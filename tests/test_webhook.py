import os
import tempfile
from shutil import rmtree

import pytest
import responses
from faker import Faker
from flask import Response, Flask
from flask.testing import FlaskClient

from statuspage2slack.statuspage_constants import ComponentStatus, \
    IncidentStatus, IncidentImpact

fake = Faker()

STATUSPAGE_DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%SZ'

test_file_path = os.path.realpath(__file__)
test_file_folder = os.path.dirname(test_file_path)


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
def incident_update_request(incident_update, incident_impact, incident_status):
    creation_datetime = fake.past_datetime()
    monitoring_datetime = fake.past_datetime(start_date=creation_datetime)
    resolved_datetime = fake.past_datetime(start_date=creation_datetime)
    update_datetime = fake.past_datetime(start_date=creation_datetime)

    name = fake.sentence(nb_words=6, variable_nb_words=True,
                         ext_word_list=None)

    return {
        "incident": {
            "backfilled": False,
            "created_at":
                creation_datetime.strftime(STATUSPAGE_DATETIME_FORMAT),
            "impact": incident_impact.value,
            "impact_override": None,
            "monitoring_at":
                monitoring_datetime.strftime(STATUSPAGE_DATETIME_FORMAT),
            "resolved_at":
                resolved_datetime.strftime(STATUSPAGE_DATETIME_FORMAT),
            "shortlink": fake.url(),
            "status": incident_status.value,
            "updated_at": update_datetime.strftime(STATUSPAGE_DATETIME_FORMAT),
            "name": name,
            "incident_updates": [incident_update]
        }
    }


@pytest.fixture()
def incident_update(incident_status):
    body = fake.paragraph()
    creation_datetime = fake.past_datetime()
    display_datetime = fake.past_datetime(start_date=creation_datetime)
    update_datetime = fake.past_datetime(start_date=creation_datetime)

    return {
        "body": body,
        "created_at": creation_datetime.strftime(STATUSPAGE_DATETIME_FORMAT),
        "display_at": display_datetime.strftime(STATUSPAGE_DATETIME_FORMAT),
        "status": incident_status.value,
        "updated_at": update_datetime.strftime(STATUSPAGE_DATETIME_FORMAT),
    }


@pytest.mark.parametrize("old_component_status", ComponentStatus)
@pytest.mark.parametrize("new_component_status", ComponentStatus)
def test_component_update(flask_client: FlaskClient,
                          component_update_request, used_templates,
                          request_mocker: responses.RequestsMock):
    response: Response = flask_client.post('/', json=component_update_request)

    assert 200 <= response.status_code < 300

    assert len(used_templates) == 1
    (template, context) = used_templates.pop()
    assert template.name == 'component_update.json'
    component_update = component_update_request['component_update']
    component = component_update_request['component']
    assert context['component_update'] == component_update
    assert context['component'] == component


@pytest.mark.parametrize("incident_status", IncidentStatus)
@pytest.mark.parametrize("incident_impact", IncidentImpact)
def test_incident_update(flask_client: FlaskClient, incident_update_request,
                         used_templates):
                         #request_mocker: responses.RequestsMock):
    response: Response = flask_client.post('/', json=incident_update_request)

    assert 200 <= response.status_code < 300

    assert len(used_templates) == 1
    (template, context) = used_templates.pop()
    assert template.name == 'incident_update.json'
    assert context['incident'] == incident_update_request['incident']


def test_invalid_request(flask_client: FlaskClient):
    response: Response = flask_client.post('/', data='dummy')
    assert 400 <= response.status_code < 500


@pytest.mark.parametrize("old_component_status",
                         [ComponentStatus.DEGRADED_PERFORMANCE])
@pytest.mark.parametrize("new_component_status", [ComponentStatus.OPERATIONAL])
@pytest.mark.parametrize("incident_status", [IncidentStatus.MONITORING])
@pytest.mark.parametrize("incident_impact", [IncidentImpact.CRITICAL])
@pytest.mark.parametrize("flag", ['COMPONENT_MESSAGES_ENABLED',
                                  'INCIDENT_MESSAGES_ENABLED'])
def test_false_enabled_flags(flask_app: Flask, flask_client: FlaskClient,
                             component_update_request, incident_update_request,
                             used_templates, flag):
    flask_app.config.update({
        flag: False
    })
    if flag == 'INCIDENT_MESSAGES_ENABLED':
        response: Response = flask_client.post('/',
                                               json=incident_update_request)
    elif flag == 'COMPONENT_MESSAGES_ENABLED':
        response: Response = flask_client.post('/',
                                               json=component_update_request)
    else:
        assert False, "Unexpected flag value"

    assert 200 <= response.status_code < 300
    assert len(used_templates) == 0


@pytest.mark.parametrize("incident_status", [IncidentStatus.MONITORING])
@pytest.mark.parametrize("incident_impact", [IncidentImpact.CRITICAL])
@pytest.mark.parametrize("env_dict", [
    {'TEMPLATE_FOLDER': test_file_folder + '/templates'}
])
def test_change_template_folder(change_env, flask_client: FlaskClient,
                                incident_update_request, used_templates,
                                request_mocker: responses.RequestsMock,
                                env_dict):
    template_name = 'incident_update.json'
    response: Response = flask_client.post('/', json=incident_update_request)
    assert 200 <= response.status_code < 300

    assert len(used_templates) == 1
    (template, context) = used_templates.pop()
    assert template.name == template_name
    assert os.path.realpath(template.filename) == os.path.realpath(
        env_dict['TEMPLATE_FOLDER'] + '/' + template_name)


def test_copy_templates(flask_app: Flask):
    runner = flask_app.test_cli_runner()
    folder = tempfile.gettempdir() + '/templates/'
    rmtree(folder, ignore_errors=True)
    result = runner.invoke(args=['webhook', 'copy-templates', folder])
