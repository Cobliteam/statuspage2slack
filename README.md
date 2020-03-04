# statuspage2slack

Customized slack messages for Atlassian Statuspage
[webhook notifications](https://help.statuspage.io/help/webhook-notifications)

| You need to sign a [Startup or higher plan](https://www.statuspage.io/pricing?tab=public) in order to enable webhooks notifications|
| --- |

# Using it ...

Create an [incoming webhook](https://cobli.slack.com/apps/A0F7XDUAZ-incoming-webhooks)
for a slack channel of your preference.

# ... as a standalone Flask app
Create a your project folder, a virtual environment for it, and install statuspage2slack

```bash
mkdir my-incident-handler && cd my-incident-handler
virtualenv -p python3 venv
source venv/bin/activate
pip install git+https://github.com/Cobliteam/statuspage2slack
```

Create a .env file with your incoming webhook url and message filter
preferences inside your project root folder
```..env
FLASK_APP=statuspage2slack 
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/XXXXXXXXX/YYYYYYYYYY/ZZZZZZZZZZZZZZZZZZZZZ
COMPONENT_MESSAGES_ENABLED=true # enable/disable component updates from Statuspage
INCIDENT_MESSAGES_ENABLED=true # enable/disable incident updates from Statuspage
```

Run you flask app
```bash
flask run --host=0.0.0.0
 * Serving Flask app "statuspage2slack"
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
```

Subscribe your project endpoint in any Statuspage as webhook

# Customized templates
Run `flask webhook copy-templates my-template-folder/`. This command copies
template files to `my-template-folder`

Template files are in [jinja](https://palletsprojects.com/p/jinja/), and are
used to create [Slack messages payloads](https://api.slack.com/reference/messaging/payload).
There are two of them:
* `incident_update.json`: generate slack messages from Statuspage incident
update notifications.`incident` key entry from 
[webhook notifications](https://help.statuspage.io/help/webhook-notifications)
(see **Incident Updates**) is available as template variable
* `component_update.json`: generate slack messages from Statuspage component
update notifications. `component_update` and `component` key entry from 
[webhook notifications](https://help.statuspage.io/help/webhook-notifications)
(see **Component Updates**) are available as template variable

Set `TEMPLATE_FOLDER` environment variable (or add a `.env` entry) pointing
to your custom template folder.
 ```bash
TEMPLATE_FOLDER=my-template-folder/ flask run --host=0.0.0.0
 * Serving Flask app "statuspage2slack"
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
```
