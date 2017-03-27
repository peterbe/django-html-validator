#!/usr/bin/env python

import re
import codecs
import os

# Prevent spurious errors during `python setup.py test`, a la
# http://www.eby-sarna.com/pipermail/peak/2010-May/003357.html:
try:
    import multiprocessing
except ImportError:
    pass


from setuptools import setup


def read(*parts):
    with codecs.open(
        os.path.join(os.path.dirname(__file__), *parts),
        encoding='utf-8'
    ) as f:
        return f.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')


def find_install_requires():
    return [x.strip() for x in
            read('requirements.txt').splitlines()
            if x.strip() and not x.startswith('#')]


README = read('README.md')

setup(
    name='django-html-validator',
    version=find_version('htmlvalidator', '__init__.py'),
    url='https://github.com/peterbe/django-html-validator',
    author='Peter Bengtsson',
    author_email='mail@peterbe.com',
    description="Yo! Check your HTML!",
    long_description=README,
    packages=['htmlvalidator'],
    license='MPL v2.0',
    include_package_data=True,
    install_requires=find_install_requires(),
    test_suite="runtests.runtests",
    zip_safe=False,
    classifiers=[
        'Framework :: Django',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'Operating System :: OS Independent',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
