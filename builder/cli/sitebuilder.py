'''Sitebuilder

Usage:
    sitebuilder build
    sitebuilder deploy [--delete]
    sitebuilder new [--title=<TITLE> --draft]
    sitebuilder serve [--debug --host=<HOST> --port=<PORT>]
    sitebuilder test

Options:
    --title=<TITLE>
    --draft
    -D --debug        start the server in debug mode
    -H --host=<HOST>  start the webserver on the given host [default: 0.0.0.0]
    -p --port=<PORT>  start the webserver on port NUM [default: 8000]
'''

import os
import codecs
import re
import sys
import twitter
import bitly_api
import logging

from boto.s3.connection import S3Connection
from boto.s3.key import Key
from ConfigParser import SafeConfigParser, NoSectionError
from docopt import docopt
from datetime import datetime

from urlparse import urljoin
from urllib import quote


from builder.app import (
    create_app,
    create_freezer
)

from builder.util import (
    slugify,
    get_file_path
)

logger = logging.getLogger(__name__)

cfg = None


def _get_cfg(app):
    global cfg
    if cfg is None:
        cfg = SafeConfigParser()
        cfg.read(app.config['API_CONFIG'])
    return cfg


def new_blog_post_tweet(app, new_post):
    '''Hook into twitter api to publish a tweet with link to new blog post'''
    cfg = _get_cfg(app)
    bitly_cred = dict(cfg.items('bitly'))
    tw_cred = dict(cfg.items('twitter'))

    file_path = new_post.name.split('/')[-1].split('.')[0]
    title = None
    new_post.seek(0)
    match = re.search(r'^[Tt]itle:\s*(.*)$', new_post.read(), re.MULTILINE)
    if match:
        try:
            title = unicode(match.group(1), 'ascii')
        except IndexError:
            print 'regex did not work properly...exiting'
    else:
        print 'blank post: {}'.format(title)
        return

    if title:
        intro = 'New blog post:'
        long_url = urljoin(app.PUBLISH_URL, file_path)
        bitly_app = bitly_api.Connection(**bitly_cred)
        tw_app = twitter.Api(**tw_cred)
        shurl = bitly_app.shorten(long_url)
        tweet = ' '.join([intro, title, shurl['url']])

        logger.debug('About to tweet this: %s', tweet)
        if not app.debug:
            tw_app.PostUpdate(tweet)


# CLI API
def build(app):
    ''' Builds this site.
    '''
    print 'Starting website build'
    app.debug = False
    app.config['ASSETS_DEBUG'] = False
    freezer = create_freezer(app)
    freezer.freeze()
    print 'Build is complete.'


def _get_files_for_deploy(build_dir):
    for dirpath, dirnames, filenames in os.walk(build_dir):
        current = os.path.basename(dirpath)
        # ignore hidden directories
        if current.startswith('.'):
            _, filenames = [], []
            continue
        # ignore un min/uglifed js and javascripts
        elif 'javascripts' in dirpath:
            _, filenames = [], []
            continue
        elif 'stylesheets' in dirpath:
            _, filenames = [], []
            continue
        for f in filenames:
            # ignore hidden filenames
            if f.startswith('.'):
                continue
            local_path = os.path.join(dirpath, f)
            # keyname is relative to the build directory
            # i.e., ~/src/blog/blog/build/foo/bar.html becomes
            # bar/foo.html and src/blog/blog/build/index.html
            # becomes index.html
            keyname = os.path.relpath(local_path, build_dir)
            yield keyname, local_path


def deploy(app, delete=False, dry_run=True):
    build(app)
    files = _get_files_for_deploy(app.config['FREEZER_DESTINATION'])
    # TODO: this should be factored out into
    # a class for managing 3rd party plugins
    cfg = _get_cfg(app)
    try:
        s3 = dict(cfg.items('s3'))
    except NoSectionError:
        logger.exception('No api credentials configured for %s', 's3')
        sys.exit(1)

    conn = S3Connection(s3['aws_access_key_id'], s3['aws_secret_access_key'])
    bucket = conn.get_bucket(s3['bucket_name'])
    if delete:
        for key in bucket.list():
            if not key.name.startswith('logs/'):
                print 'Deleting {}'.format(key.name)
                if not dry_run:
                    key.delete()

    for keyname, localpath in files:
        if not dry_run:
            k = Key(bucket)
            k.key = quote(keyname)
            k.set_contents_from_filename(localpath)
        print 'Set key contents for {}'.format(keyname)

    print 'Succesful deployment, done!'


def new(app, draft=True, title=None, section='posts', filename=None):
    ''' Create a new empty post.

    :kwarg: draft (bool) - should the page be marked as published or not. Defaults to false
    :kwarg: title (str) - The unescaped title for the new post or page
    :kwarg: section(str) - Which section to put the new writing in. Options are currently 'pages' or 'posts'.
    :kwarg: filename (str) - file name to be used. If not supplied, one will be determined based on title
    '''
    post_date = datetime.today()
    title = unicode(title) if title else u'Untitled Post'
    if not filename:
        filename = u'%s.md' % slugify(title)
    pathargs = [section, filename, ]
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
        logger.info(u'Created %s' % filepath)
    except Exception:
        print 'Problem writing to {}'.format(filepath)
        raise


def serve(app, host='0.0.0.0', port=8000, debug=False):
    ''' Serves this site.
    '''
    app.config['ASSETS_DEBUG'] = debug
    app.debug = debug
    if not app.debug:
        import logging
        from logging import FileHandler
        file_handler = FileHandler('error.log')
        file_handler.setLevel(logging.WARNING)
        app.logger.addHandler(file_handler)
    app.run(host=host, port=port, debug=debug)


def main():
    app = create_app()
    arguments = docopt(__doc__)
    if arguments['build']:
        build(app)
    elif arguments['deploy']:
        deploy(app, delete=arguments.get('--delete', True))
    elif arguments['serve']:
        serve(app, host=arguments.get('--host', '0.0.0.0'),
              port=int(arguments.get('--port', 8000)), debug=arguments.get('--debug', False))
    elif arguments['new']:
        new(app, title=arguments.get('--title'), draft=arguments.get('--draft', True))
    else:
        raise Exception('Something went wrong with your docopt')

if __name__ == '__main__':
    main()
