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

from sentry.utils.http import absolute_uri
from django.core.urlresolvers import reverse

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


class DingtalkForm(notify.NotificationConfigurationForm):
    urls = forms.CharField(
        label=_('Dingtalk robot url'),
        widget=forms.Textarea(attrs={
            'class': 'span6', 'placeholder': 'https://oapi.dingtalk.com/robot/send?access_token=9bacf9b193f'}),
        help_text=_('Enter dingtalk robot url.'))

    def clean_url(self):
        value = self.cleaned_data.get('url')
        return validate_urls(value)

 
class DingtalkPlugin(notify.NotificationPlugin):
    author = 'guoyong yi'
    author_url = 'https://github.com/gzhappysky/sentry-dingtalk'
    version = sentry.VERSION
    description = "Integrates dingtalk robot."
    resource_links = [
        ('Bug Tracker', 'https://github.com/gzhappysky/sentry-dingtalk/issues'),
        ('Source', 'https://github.com/gzhappysky/sentry-dingtalk'),
    ]

    slug = 'dingtalk'
    title = 'dingtalk'
    conf_title = title
    conf_key = 'dingtalk'  

    project_conf_form = DingtalkForm
    timeout = getattr(settings, 'SENTRY_DINGTALK_TIMEOUT', 3) 
    logger = logging.getLogger('sentry.plugins.dingtalk')

    def is_configured(self, project, **kwargs):
        return bool(self.get_option('urls', project))

    def get_config(self, project, **kwargs):
        return [{
            'name': 'urls',
            'label': 'dingtalk robot url',
            'type': 'textarea',
            'help': 'Enter dingtalk robot url.',
            'placeholder': 'https://oapi.dingtalk.com/robot/send?access_token=9bacf9b193f',
            'validators': [validate_urls],
            'required': False
        }] 

    def get_webhook_urls(self, project):
        url = self.get_option('urls', project)
        if not url:
            return ''
        return url 

    def send_webhook(self, url, payload):
        return safe_urlopen(
            url=url,
            json=payload,
            timeout=self.timeout,
            verify_ssl=False,
        )

    def get_group_url(self, group):
        return absolute_uri(reverse('sentry-group', args=[
            group.team.slug,
            group.project.slug,
            group.id,
        ]))

    def notify_users(self, group, event, fail_silently=False): 
        url = self.get_webhook_urls(group.project)
        link = self.get_group_url(group)
        message_format = '[%s] %s (%s)'
        message = message_format % (event.server_name, event.message, link)
        data = {"msgtype": "text",
                    "text": {
                        "content": message
                    }
                }
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        r = requests.post(url, data=json.dumps(data), headers=headers)

 