import os

from urllib.parse import urljoin
from tempfile import gettempdir

# Flask Configuration
BASE_URL = os.getenv('BLOG_BASE_DIR', 'https://cameronlane.org')
PUBLISH_URL = urljoin(BASE_URL, os.getenv('BLOG_PUBLISH_URL', 'blog/posts/'))

# flask-flatpages
FLATPAGES_AUTO_RELOAD = True
FLATPAGES_ROOT = os.path.join(os.path.dirname(__file__), 'pages')
FLATPAGES_EXTENSION = '.md'
FLATPAGES_MARKDOWN_EXTENSIONS = ['fenced_code', 'footnotes', 'codehilite']

# flask-freezer
FREEZER_BASE_URL = BASE_URL
FREEZER_REMOVE_EXTRA_FILES = True
FREEZER_DESTINATION = os.getenv('BLOG_BUILD_DIR', os.path.join(gettempdir(), 'blog_build'))
FREEZER_STATIC_IGNORE = ['javascripts/*', '*.styl', '*.scss', 'stylesheets/*']

# assets pipeline
ASSETS_DEBUG = True

# APP configuration
FEED_MAX_LINKS = 25
SECTION_MAX_LINKS = 12

# DEPLOYMENT Configuration
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', None)
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', None)
S3_BUCKET = os.getenv('S3_BUCKET', 'cameronlane.org')
