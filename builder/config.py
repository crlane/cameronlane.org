import os
from urlparse import urljoin

# Flask Configuration
BASE_URL = 'https://cameronlane.org'
PUBLISH_URL = urljoin(BASE_URL, 'blog/posts/')

# flask-flatpages
FLATPAGES_AUTO_RELOAD = True
FLATPAGES_ROOT = os.path.join(os.path.dirname(__file__), 'pages')
FLATPAGES_EXTENSION = '.md'
FLATPAGES_MARKDOWN_EXTENSIONS = ['fenced_code', 'footnotes', 'codehilite']

# flask-freezer
FREEZER_BASE_URL = BASE_URL
FREEZER_REMOVE_EXTRA_FILES = True
FREEZER_DESTINATION = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'build')

# assets pipeline
ASSETS_DEBUG = True

# App configuration
# config specific to this application
FEED_MAX_LINKS = 25
SECTION_MAX_LINKS = 12
API_CONFIG = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'apis.cfg')
