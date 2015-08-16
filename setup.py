try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'AEM Command Line Tool',
    'author': 'Björn Skoglund',
    'url': 'http://twitter.com/bjosk',
    ## 'download_url': 'Where to download it.',
    'author_email': 'bjorn.skoglund@valtech.com',
    'version': '0.1',
    'install_requires': ['nose', 'requests'],
    'packages': ['acmd'],
    'scripts': [],
    'name': 'aem-cmd'
}

setup(**config)
