# -*- coding: utf-8 -*-
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': "Get Debian packaging information of dependencies of a \
            Ruby application/library",
    'author': 'Balasankar C',
    'url': 'https://gitlab.com/balasankarc/gemdeps',
    'download_url': 'https://gitlab.com/balasankarc/gemdeps',
    'author_email': 'balasankarc@autistici.org',
    'version': '1.0.0',
    'license': 'GPL-3+',
    'long_description': '''
Installation
~~~~~~~~~~~~

::

    git clone https://github.com/balasankarc/gemdeps.git
    cd gemdeps
    python setup.py install


Copyright
~~~~~~~~~

2015 Balasankar C balasankarc@autistici.org

License
~~~~~~~

gemdeps is released under `GNU GPL version 3 (or above) License`_.

.. _GNU GPL version 3 (or above) License: http://www.gnu.org/licenses/gpl
''',
    'packages': ['gemdeps'],
    'scripts': ['bin/gemdeps'],
    'name': 'gemdeps'
}

setup(
    classifiers=[
        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
    ], **config)
