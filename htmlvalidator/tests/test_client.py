# -*- coding: utf-8 -*-

import codecs
import os
import shutil
import sys
import tempfile
from glob import glob

import requests
from mock import Mock, patch

from htmlvalidator import client
from htmlvalidator.tests import TestCase


class ClientTestCase(TestCase):

    def setUp(self):
        super(ClientTestCase, self).setUp()
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir)
        super(ClientTestCase, self).tearDown()

    def _response(self, **kwargs):
        return Mock(spec=requests.Response, **kwargs)

    @patch('htmlvalidator.core.requests.post')
    def test_get(self, post):

        content = (
            u'Error: End tag “h2” seen, but there were open elements.\n'
            u'From line 8, column 12; to line 8, column 16\n'
            u'There were errors. (Tried in the text/html mode.)'
        )
        post.return_value = self._response(
            text=content,
            status_code=200
        )

        c = client.ValidatingClient()
        response = c.get('/view/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            '<title>Hi!</title>' in response.content.decode('utf-8')
        )

        with self.settings(
            HTMLVALIDATOR_ENABLED=True, HTMLVALIDATOR_DUMPDIR=self.tmpdir
        ):
            response = c.get('/view/')
            self.assertEqual(response.status_code, 200)
            self.assertTrue(
                '<title>Hi!</title>' in response.content.decode('utf-8')
            )
            html_file, = glob(os.path.join(self.tmpdir, '*.html'))
            with codecs.open(html_file, encoding='utf-8') as f:
                self.assertEqual(f.read(), response.content.decode('utf-8'))
            txt_file, = glob(os.path.join(self.tmpdir, '*.txt'))
            with codecs.open(txt_file, encoding='utf-8') as f:
                self.assertTrue(content in f.read())

        # Make sure the "headers" argument to htmlvalidator.core.requests.post
        # was a mapping of str to str.
        using_python_2 = sys.version_info[0] < 3
        bytestype = str if using_python_2 else bytes
        stringtype = unicode if using_python_2 else str
        post.assert_called()
        headers = post.call_args[1]['headers']
        for header in headers:
            self.assertTrue(isinstance(header, stringtype) or
                            isinstance(header, bytestype))
            self.assertTrue(isinstance(headers[header], stringtype) or
                            isinstance(headers[header], bytestype))
