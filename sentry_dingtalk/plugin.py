"""
sentry_dingtalk.models
~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2017 by Guoyong yi, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from __future__ import absolute_import

import time
import json
import requests
import logging
import six
import sentry

from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from sentry.exceptions import PluginError
from sentry.plugins.bases import notify
from sentry.http import is_valid_url, safe_urlopen
from sentry.utils.safe import safe_execute


def validate_urls(value, **kwargs):
    output = []
    for url in value.split('\n'):
        url = url.strip()
        if not url:
            continue
        if not url.startswith(('http://', 'https://')):
            raise PluginError('Not a valid URL.')
        if not is_valid_url(url):
            raise PluginError('Not a valid URL.')
        output.append(url)
    return '\n'.join(output)


class WebHooksOptionsForm(notify.NotificationConfigurationForm):
    urls = forms.CharField(
        label=_('Dingtalk robot url'),
        widget=forms.Textarea(attrs={
            'class': 'span6', 'placeholder': 'https://sentry.io/callback/url'}),
        help_text=_('Enter dingtalk robot url.'))

    def clean_url(self):
        value = self.cleaned_data.get('url')
        return validate_urls(value)


class DingtalkPlugin(notify.NotificationPlugin):
    author = 'NewBee Team'
    author_url = 'https://github.com/gzhappysky/sentry-dingtalk'
    version = sentry.VERSION
    description = "Integrates dingtalk robot."
    resource_links = [
        ('Bug Tracker', 'https://github.com/getsentry/sentry/issues'),
        ('Source', 'https://github.com/getsentry/sentry'),
    ]

    slug = 'dingtalk'
    title = 'dingtalk'
    conf_title = title
    conf_key = 'dingtalk'
    # TODO(dcramer): remove when this is migrated to React
    project_conf_form = WebHooksOptionsForm
    timeout = getattr(settings, 'SENTRY_WEBHOOK_TIMEOUT', 3)
    logger = logging.getLogger('sentry.plugins.webhooks')
    user_agent = 'sentry-webhooks/%s' % version

    def is_configured(self, project, **kwargs):
        return bool(self.get_option('urls', project))

    def get_config(self, project, **kwargs):
        return [{
            'name': 'urls',
            'label': 'Callback URLs',
            'type': 'textarea',
            'help': 'Enter callback URLs to POST new events to (one per line).',
            'placeholder': 'https://sentry.io/callback/url',
            'validators': [validate_urls],
            'required': False
        }]

    def get_group_data(self, group, event):
        data = {
            'id': six.text_type(group.id),
            'project': group.project.slug,
            'project_name': group.project.name,
            'logger': event.get_tag('logger'),
            'level': event.get_tag('level'),
            'culprit': group.culprit,
            'message': event.get_legacy_message(),
            'url': group.get_absolute_url(),
        }
        data['event'] = dict(event.data or {})
        data['event']['tags'] = event.get_tags()
        return data

    def get_webhook_urls(self, project):
        urls = self.get_option('urls', project)
        if not urls:
            return ()
        return filter(bool, urls.strip().splitlines())

    def send_webhook(self, url, payload):
        return safe_urlopen(
            url=url,
            json=payload,
            timeout=self.timeout,
            verify_ssl=False,
        )

    def notify_users(self, group, event, fail_silently=False):
        url = "https://oapi.dingtalk.com/robot/send?access_token=9bacf9b193fe44607b52486590727a4702ec87c5adbc5854d73f747b393528b1"
        data = {"msgtype": "text", 
                    "text": {
                        "content": 'message'
                    }
                }
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        r = requests.post(url, data=json.dumps(data), headers=headers)





# import time
# import json
# import requests

# from django import forms
# from django.core.urlresolvers import reverse

# from sentry.exceptions import PluginError
# from sentry.plugins.bases import notify
# from sentry.http import is_valid_url, safe_urlopen
# from sentry.utils.safe import safe_execute
# from sentry.plugins import register

# # import sentry_whatsapp 
        

# class DingtalkForm(notify.NotificationConfigurationForm):
#     dingRobotUrl = forms.CharField(required=True, help_text="Your ding robot url.") 


# class DingtalkPlugin(notify.NotificationPlugin):
#     author = 'Guoyong yi'
#     author_url = 'https://github.com/gzhappysky/sentry-dingtalk'
#     title = 'Dingtalk'
#     conf_title = 'Dingtalk'
#     conf_key = 'Dingtalk'
#     version = '0.1.0'
#     project_conf_form = DingtalkForm


#     def is_configured(self, project, **kwargs):
#         return bool(self.get_option('dingRobotUrl', project))
    
#     def get_config(self, project, **kwargs):
#         return [{
#             'name': 'ding_talk',
#             'label': 'Callback URLs',
#             'type': 'textarea',
#             'help': 'Enter callback URLs to POST new events to (one per line).',
#             'placeholder': 'https://sentry.io/callback/url',
#             'validators': [validate_urls],
#             'required': False
#         }]

#     def notify_users(self, group, event, fail_silently=False):
#         send_payload(self,group.project,'hello sentry')

#     def send_payload(self, project, message):
#         url = "https://oapi.dingtalk.com/robot/send?access_token=9bacf9b193fe44607b52486590727a4702ec87c5adbc5854d73f747b393528b1"
#         data = {"msgtype": "text", 
#                     "text": {
#                         "content": message
#                     }
#                 }
#         headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
#         r = requests.post(url, data=json.dumps(data), headers=headers)
        

# register(DingtalkPlugin)