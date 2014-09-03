import codecs
import os
import tempfile
import StringIO
import gzip
import re

import requests

from django.conf import settings

from .exceptions import ValidatorOperationalError, ValidationError


def validate_html(html, encoding, filename,
                  (args, kwargs)):
    temp_dir = getattr(
        settings,
        'HTMLVALIDATOR_DUMPDIR',
        None
    )
    if temp_dir is None:
        temp_dir = os.path.join(
            tempfile.gettempdir(), 'outputtestingclient'
        )
    if not os.path.isdir(temp_dir):
        os.mkdir(temp_dir)
    temp_file = os.path.join(
        temp_dir,
        filename
    )
    with codecs.open(temp_file, 'w', encoding) as f:
        f.write(html)
        valid = _validate(temp_file, encoding, (args, kwargs))
    if valid:
        os.remove(temp_file)


def _validate(html_file, encoding, (args, kwargs)):
    buf = StringIO.StringIO()
    gzipper = gzip.GzipFile(fileobj=buf, mode='wb')
    with codecs.open(html_file, 'r', encoding) as f:
        gzipper.write(f.read())
        gzipper.close()
    gzippeddata = buf.getvalue()
    buf.close()

    req = requests.post(
        'http://html5.validator.nu/?out=text',
        headers={
            'Content-Type': 'text/html',
            'Accept-Encoding': 'gzip',
            'Content-Encoding': 'gzip',
            'Content-Length': len(gzippeddata),
        },
        data=gzippeddata
    )

    if req.status_code != 200:
        raise ValidatorOperationalError(req)

    raise_exceptions = getattr(
        settings,
        'HTMLVALIDATOR_FAILFAST',
        False
    )

    messages = []
    for block in re.split('\n\n+', req.content):
        messages.append(block)

    if req.content and 'The document is valid' not in req.content:
        print "VALIDATON TROUBLE"
        print "To debug, see:"
        print "\t", html_file
        txt_file = re.sub('\.html$', '.txt', html_file)
        assert txt_file != html_file
        print "\t", txt_file
        with codecs.open(txt_file, 'w', encoding) as f:
            f.write('Arguments to GET:\n')
            for arg in args:
                f.write('\t%s\n' % arg)
            for k, w in kwargs.items():
                f.write('\t%s=%s\n' % (k, w))
            f.write('\n')
            f.write(unicode(req.content, encoding))
        if raise_exceptions:
            raise ValidationError(req.content)
