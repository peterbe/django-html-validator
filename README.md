django-html-validator
=====================

[![Build Status](https://travis-ci.org/peterbe/django-html-validator.svg?branch=master)](https://travis-ci.org/peterbe/django-html-validator)

A tool to do validation of your HTML generated from your Django app.
Python 3 compatible.

License: [MPL 2](http://www.mozilla.org/MPL/2.0/)


Warning!
--------

If you don't download a local `vnu.jar` file (see below), it will use
[validator.nu](https://validator.nu/) and **send your HTML there**.

If you use `htmlvalidator` to validate tests it's unlikely your HTML contains
anything sensitive or personally identifiable but if you use the middleware
option there's a potential risk.

Install
-------

First things first, very simple:

    pip install django-html-validator

Note, it won't do anything until you chose how you want to use it and you also
need to explicitly enable it with a setting.

Basically, you have a choice of how you want to use this:

* As a middleware
* In your unit tests (technically they're integration tests in Django)

If you chose to set it up as a middleware and enable it accordingly it will
run for every rendered template in the tests too. Not just when you run the
server.

Settings
--------

Independent of how you use `htmlvalidator` you need to switch it on.
It's not on by default. The setting to do that is:

```python
HTMLVALIDATOR_ENABLED = True
```

What this does, is that it prints all validation errors to `stdout`.
But it doesn't stop the execution from running. Even if there are errors.

To make it so that the execution stops as soon as there is any validation
error switch this on in your settings:

```python
HTMLVALIDATOR_FAILFAST = True
```

Now, if there's any validation error going through the client you'll
get a `htmlvalidator.exceptions.ValidationError` exception raised.

Equally, if you're running it as a middleware and have this setting on it
will raise the exception in the request.

When validation errors and warnings are encountered, `htmlvalidator` will
dump the HTML to a file and the errors in a file with the same name except
with the extension `.txt` instead. It will dump this into, by default, the
systems tmp directory and in sub-directory called `htmlvalidator`.
E.g. `/tmp/htmlvalidator/`. If you want to override that change:

```python
HTMLVALIDATOR_DUMPDIR = '~/validationerrors/'  # default it /tmp
```
Whatever you set, the directory doesn't need to exist but its parent does.

By default when `htmlvalidator` encounters validation errors it stores
the relevant HTML file in the `HTMLVALIDATOR_DUMPDIR` together with a file
with the extension `.txt` in the same directory. Alternatively you can just let
it dump the validation errors and warnings straight onto stdout with:

```python
HTMLVALIDATOR_OUTPUT = 'stdout'  # default is 'file'
```

Setting the vnu.jar path
------------------------

By default, all validation is done by sending your HTML with HTTP POST to
[html5.validator.nu](https://html5.validator.nu/).

Not only does this put a lot of stress on their server. Especially if you have
a lot of tests. It's also slow because it depends on network latency. A much
better way is to download the `vnu.jar` file from their
[latest release](https://github.com/validator/validator/releases) on
[GitHub page](https://github.com/validator/).

You set it up simply like this:

```python
HTMLVALIDATOR_VNU_JAR = '~/downloads/vnu.jar'
```

This also **requires java to be installed** because that's how `.jar` files are
executed on the command line.

Be aware that calling this `vnu.jar` file is quite slow. Over 2 seconds is
not unusual. A faster alternative is to use the `vnu.jar` to run a local web
instance of the validator, and pointing validation to use that by *NOT* setting
`HTMLVALIDATOR_VNU_JAR` and doing this instead:

```python
HTMLVALIDATOR_VNU_URL = 'http://localhost:8888/'
```

The local web instance of the validator can be started typically by:

```
java -cp vnu.jar nu.validator.servlet.Main 8888
```

Validating during running the server
------------------------------------

A way to do HTML validation is to do it during running the
server. E.g. with `./manage.py runserver`.

To do that you need to enable the middleware. In your settings module,
append `htmlvalidator.middleware.HTMLValidator`
to `MIDDLEWARE_CLASSES` for example like this:

```python
if HTMLVALIDATOR_ENABLED:
    MIDDLEWARE_CLASSES += ("htmlvalidator.middleware.HTMLValidator",)
```

You can also add it directly and unconditionally to `MIDDLEWARE_CLASSES`
and it won't do anything (except be loaded) unless enabled, see
the note above about `HTMLVALIDATOR_ENABLED` for more info.

Also, if you enable `HTMLVALIDATOR_FAILFAST`, when running the
`htmlvalidator` middleware it will raise an exception as soon as it
sees some invalid HTML.


Validating HTML in tests
------------------------

Suppose you have a class that does tests. By default it already has a
`self.client` which you use to make requests. All you need to do is to
replace it with the `htmlvalidator.client.ValidatingClient`
class. For example:

```python

from django.test import TestCase
from htmlvalidator.client import ValidatingClient


class MyAppTests(TestCase):

    def setUp(self):
        super(MyAppTests, self).setUp()
        self.client = ValidatingClient()

    def test_homepage(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
```
