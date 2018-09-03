# coding: utf-8
from setuptools import setup

from acmd import __version__

LONG_DESC = """AEM command line management.
===============================

A set of tools to administrate an Adobe AEM content management installation
from the command line. Features include:

* Unix philosophy enables pipe and script based composition of common tasks
* Bash completion script included
* Content search, modification, deletion
* User and group management
* Package management
* Simple instance management for running a command against all your installations
* Common ops tools like repo optimization, activation and cache clearing

Full documentation at <https://github.com/bjorns/aem-cmd/blob/master/README.md>
"""

classifiers = [
    # How mature is this project? Common values are
    #   3 - Alpha
    #   4 - Beta
    #   5 - Production/Stable
    'Development Status :: 4 - Beta',

    # Indicate who your project is intended for
    'Intended Audience :: Developers',
    'Topic :: Software Development',

    # Pick your license as you wish (should match "license" above)
    'License :: OSI Approved :: MIT License',

    # Specify the Python versions you support here. In particular, ensure
    # that you indicate whether you support Python 2, Python 3 or both.
    'Programming Language :: Python :: 2.7',
    "Programming Language :: Python :: 3.6"
]

config = {
    'name': 'aem-cmd',
    'version': __version__,
    'description': 'AEM Command line tools',
    'long_description': LONG_DESC,
    'license': 'MIT',
    'author': 'Björn Skoglund',
    'author_email': 'bjorn.skoglund@icloud.com',
    'url': 'https://github.com/bjorns/aem-cmd',
    'download_url': 'https://github.com/bjorns/aem-cmd',
    'classifiers': classifiers,

    # Build specs
    'install_requires': ['requests', 'requests-toolbelt', 'configparser', 'keyring', 'keyrings.alt'],
    'packages': ['acmd', 'acmd.tools', 'acmd.jcr', 'acmd.workflows', 'acmd.assets', 'acmd.util'],
    'package_data': {'acmd': ['data/acmd.rc.template', 'data/acmd.bash_completion']},
    'scripts': ['bin/acmd']
}

setup(**config)
