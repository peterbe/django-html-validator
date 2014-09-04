import codecs
import os
import tempfile
import StringIO
import gzip
import re
import subprocess

import requests

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

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
            tempfile.gettempdir(), 'htmlvalidator'
        )
    else:
        temp_dir = os.path.expanduser(temp_dir)
        temp_dir = os.path.abspath(temp_dir)

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

    if getattr(settings, 'HTMLVALIDATOR_VNU_JAR', None):
        vnu_jar_path = settings.HTMLVALIDATOR_VNU_JAR
        vnu_jar_path = os.path.expanduser(vnu_jar_path)
        vnu_jar_path = os.path.abspath(vnu_jar_path)
        if not os.path.isfile(vnu_jar_path):
            raise ImproperlyConfigured(
                '%s is not a file' % vnu_jar_path
            )
        status, out, err = _run_command(
            'java -jar {} {}'.format(vnu_jar_path, html_file)
        )
        if status not in (0, 1):
            # 0 if it worked and no validation errors/warnings
            # 1 if it worked but there was validation errors/warnings
            raise ValidatorOperationalError(err)

        # out = unicode(out, 'utf-8')
        err = unicode(err, 'utf-8')
        output = err  # cryptic, I know
        output = re.sub(
            '"file:%s":' % re.escape(html_file),
            '',
            output
        )

    else:
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

        output = unicode(req.content, encoding)

    raise_exceptions = getattr(
        settings,
        'HTMLVALIDATOR_FAILFAST',
        False
    )

    how_to_ouput = getattr(
        settings,
        'HTMLVALIDATOR_OUTPUT',
        'file'
    )
    if output and 'The document is valid' not in output:
        print "VALIDATON TROUBLE"
        if how_to_ouput == 'stdout':
            print output
            print
        else:
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
                f.write(output)

        if raise_exceptions:
            raise ValidationError(output)


def _run_command(command):
    # print "COMMAND"
    # print command
    proc = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    out, err = proc.communicate(input=input)
    return proc.returncode, out.strip(), err.strip()
