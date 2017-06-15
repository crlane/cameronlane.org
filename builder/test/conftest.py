import os
import pytest

from datetime import datetime

from builder.app import create_app
from builder.cli import sitebuilder


@pytest.fixture(scope='session')
def tmp_api_cfg(tmpdir_factory):
    wd = tmpdir_factory.mktemp('config').join('apis.cfg')
    return wd


@pytest.fixture(scope='function')
def s3_config(tmp_api_cfg):
    creds = dict(section='s3', values=dict(
        aws_access_key_id='foo',
        aws_secret_access_key='bar',
        bucket_name='example.com')
    )
    section = '[{}]'.format(creds['section'])
    keys = ['{}={}'.format(k, v) for k, v in creds['values'].items()]
    tmp_api_cfg.write('\n'.join([section] + keys))
    return tmp_api_cfg


@pytest.fixture(scope='session')
def tmp_build(tmpdir_factory):
    wd = tmpdir_factory.mktemp('build')
    return wd


@pytest.fixture(scope='function')
def creates_posts(request, tmp_pages):
    expected = ['this-post-is-published.md', 'this-post-is-a-draft.md']

    def _reset_posts():
        posts = tmp_pages.join('posts')
        for p in posts.visit():
            if p.basename not in expected:
                p.remove()
    request.addfinalizer(_reset_posts)


@pytest.fixture(scope='session', autouse=True)
def tmp_pages(tmpdir_factory, page_template, draft_post, published_post):
    now = datetime.now()
    wd = tmpdir_factory.mktemp('pages')
    for page in ['home', 'resume', 'contact']:
        p = wd.ensure('{}.md'.format(page))
        page_data= page_template.format(
            **{'title':page, 'date_': now.strftime('%Y-%m-%d'),
                'published': True, 'type_': 'page', 'tags': '', 'content': '# {}'.format(page)})
        p.write(page_data)

    published = wd.ensure('posts', 'this-post-is-published.md')
    published.write(published_post)
    draft = wd.ensure('posts', 'this-post-is-a-draft.md')
    draft.write(draft_post)
    return wd


@pytest.fixture(scope='session')
def tmp_pages_path(tmp_pages):
    return os.path.join(tmp_pages.dirname, tmp_pages.basename)


@pytest.fixture(scope='session')
def tmp_api_cfg_path(tmp_api_cfg):
    return os.path.join(tmp_api_cfg.dirname, tmp_api_cfg.basename)


@pytest.fixture(scope='session')
def test_conf(request, tmp_pages_path, tmp_api_cfg_path, tmp_build):
    return {
        'DEBUG': True,
        'TESTING': True,
        'FLATPAGES_ROOT': tmp_pages_path,
        'FLATPAGES_EXTENSION': '.md',
        'FLATPAGES_MARKDOWN_EXTENSIONS': ['fenced_code', 'footnotes', 'codehilite'],
        'FLATPAGES_AUTO_RELOAD': True,
        'FREEZER_DESTINATION': tmp_build.strpath,
        'API_CONFIG': tmp_api_cfg_path
    }


@pytest.fixture(scope='session')
def test_app(test_conf):
    app = create_app(test_conf)
    return app


@pytest.fixture(scope='session')
def test_build(test_app):
    sitebuilder.build(test_app)


@pytest.fixture(scope='session')
def test_client(request, test_app):
    return test_app.test_client()


@pytest.fixture(scope='session')
def page_template():
    return u"""title: {title}
date: {date_}
published: {published}
type: {type_}
tags: {tags}

{content}"""


@pytest.fixture(scope='session')
def published_post(request, page_template):
    template = dict(
            title='This Post Exists',
            date_=datetime.today().strftime('%Y-%m-%d'),
            published=True,
            type_='post',
            tags=','.join(['foo', 'bar', 'baz']),
            content='# Hello! This is a published post'
            )

    return page_template.format(**template)


@pytest.fixture(scope='session')
def draft_post(request, page_template):
    template = dict(
            title='This Post Exists',
            date_=datetime.now().strftime('%Y-%m-%d'),
            published=False,
            type_='post',
            tags=','.join(['fizz', 'buzz', 'foo']),
            content='# Hello! This is a draft post'
            )

    return page_template.format(**template)
