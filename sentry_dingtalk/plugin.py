"""
sentry_dingtalk.models
~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2017 by Guoyong yi, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

import time
import json
import requests

from django import forms
from django.core.urlresolvers import reverse

from sentry.exceptions import PluginError
from sentry.plugins.bases import notify
from sentry.http import is_valid_url, safe_urlopen
from sentry.utils.safe import safe_execute
from sentry.plugins import register

# import sentry_whatsapp 
        

class DingtalkForm(notify.NotificationConfigurationForm):
    dingRobotUrl = forms.CharField(required=True, help_text="Your ding robot url.") 


class DingtalkPlugin(notify.NotificationPlugin):
    author = 'Guoyong yi'
    author_url = 'https://github.com/gzhappysky/sentry-dingtalk'
    title = 'Dingtalk'
    conf_title = 'Dingtalk'
    conf_key = 'Dingtalk'
    version = '0.1.0'
    project_conf_form = DingtalkForm


    def is_configured(self, project, **kwargs):
        return bool(self.get_option('dingRobotUrl', project))
    
    def get_config(self, project, **kwargs):
        return [{
            'name': 'ding_talk',
            'label': 'Callback URLs',
            'type': 'textarea',
            'help': 'Enter callback URLs to POST new events to (one per line).',
            'placeholder': 'https://sentry.io/callback/url',
            'validators': [validate_urls],
            'required': False
        }]

    def notify_users(self, group, event, fail_silently=False):
        send_payload(self,group.project,'hello sentry')

    def send_payload(self, project, message):
        url = "https://oapi.dingtalk.com/robot/send?access_token=9bacf9b193fe44607b52486590727a4702ec87c5adbc5854d73f747b393528b1"
        data = {"msgtype": "text", 
                    "text": {
                        "content": message
                    }
                }
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        r = requests.post(url, data=json.dumps(data), headers=headers)
        

register(DingtalkPlugin)