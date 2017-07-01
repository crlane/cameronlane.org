# -*- coding: utf-8 -*-
'''sitebuilder

Usage:
    sitebuilder build
    sitebuilder deploy [--delete --dry-run]
    sitebuilder new TITLE [--draft]
    sitebuilder serve [--debug --host=HOST --port=PORT]
    sitebuilder test

Options:
    -D --debug        start the server in debug mode
    -H --host=HOST  start the webserver on the given host [default: 0.0.0.0]
    -p --port=PORT  start the webserver on port NUM [default: 8000]
    --draft
    --delete
    --dry-run
'''

import os
import codecs
import sys

from datetime import datetime
from tempfile import TemporaryDirectory

from docopt import docopt


from builder.app import (
    create_app,
    create_freezer,
)

from builder.deploy import (
    Deployment,
    ConfigurationError
)

from builder.images import (
    copy_images_to_build
)

from builder.util import (
    slugify,
    get_file_path
)


# CLI API
def build(app, target_dir=None):
    """
    Builds the static app using its configuration
    """
    print('Starting website build')
    app.debug = False
    freezer = create_freezer(app)
    freezer.freeze()
    image_src_dir = os.path.join(app.config['FLATPAGES_ROOT'], 'images')
    image_dst_dir = target_dir or os.path.join(app.config['FREEZER_DESTINATION'], 'images')
    copy_images_to_build(image_src_dir, image_dst_dir)
    print('Build is complete.')


def deploy(app, delete, dry_run):
    destination = app.config['FREEZER_DESTINATION']
    print('Building site at {}'.format(destination))
    build(app)
    try:
        deploy_mgr = Deployment(app, destination)
    except ConfigurationError:
        print('No deployment credentials configured. Exiting!')
        sys.exit(1)
    deploy_mgr.deploy(delete=delete, dry_run=dry_run)
    print('Successful deployment, done!')


def new(app, draft=True, title=None, section='pages', filename=None):
    """ Create a new empty post.

    :kwarg draft: (bool) should the page be marked as published or not. Defaults to false
    :kwarg title: (str) The unescaped title for the new post or page
    :kwarg section: (str) Which section to put the new writing in. Options are currently 'pages' or 'posts'.
    :kwarg filename: (str) file name to be used. If not supplied, one will be determined based on title
    """
    post_date = datetime.today()
    title = str(title) if title else u'Untitled Post'
    if not filename:
        filename = u'%s.md' % slugify(title)
    pathargs = [filename]
    if section != 'pages':
        pathargs = [section] + pathargs
    filepath = get_file_path(app, pathargs)
    if os.path.exists(filepath):
        raise Exception('File %s exists' % filepath)
    content = '\n'.join([
        u'title: {}'.format(title),
        u'date: {}'.format(post_date.strftime('%Y-%m-%d')),
        u'type: post',
        u'published: False',
        u'tags:\n\n',
        u'# {}\n'.format(title)
    ])
    try:
        codecs.open(filepath, 'w', encoding='utf8').write(content)
        print(u'Created {}'.format(filepath))
    except Exception:
        print('Problem writing to {}'.format(filepath))
        raise


def serve(app, host='0.0.0.0', port=8000, debug=False):
    ''' Serves this site.
    '''
    app.debug = debug
    app.run(host=host, port=port, debug=debug)


def main(**kwargs):
    if not kwargs:
        kwargs = docopt(__doc__)
    app = create_app()
    if kwargs['build']:
        build(app)
    elif kwargs['deploy']:
        deploy(app, kwargs.get('--delete'), kwargs.get('--dry-run'))
    elif kwargs['serve']:
        host = kwargs.get('--host', '0.0.0.0')
        port = int(kwargs.get('--port'))
        debug = kwargs.get('--debug')
        serve(app, host=host, port=port, debug=debug)
    elif kwargs['new']:
        new(app, title=kwargs.pop('TITLE'), draft=kwargs.get('--draft'))
    else:
        raise Exception('Something went wrong with your docopt')
