import inspect
import tempfile
import codecs
import os
import re

import requests
from django.test.client import Client
from django.conf import settings

from .utils import find_charset_encoding
from .core import validate_html


class ValidatingClient(Client):

    def get(self, *args, **kwargs):
        response = super(ValidatingClient, self).get(*args, **kwargs)
        enabled = getattr(
            settings,
            'HTMLVALIDATOR_ENABLED',
            False
        )
        if not enabled:
            return response

        # perhaps you already, for some reason have the middleware installed
        if (
            'htmlvalidator.middleware.HTMLValidator'
            in settings.MIDDLEWARE_CLASSES
        ):
            # no point doing it here too
            return response

        caller = inspect.stack()[1]
        caller_line = caller[2]
        caller_name = caller[3]

        if (
            response['Content-Type'].startswith('text/html')
            and
            response.status_code == 200
        ):
            encoding = find_charset_encoding(response['Content-Type'])
            if not response.content:
                raise ValueError('No response.content', args[0])

            validate_html(
                response.content,
                encoding,
                '%s-%s.html' % (caller_name, caller_line),
                (args, kwargs)
            )
        return response
