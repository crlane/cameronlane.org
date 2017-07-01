import os
import pytest
import shutil

from datetime import datetime

from builder.app import create_app
from builder.cli import sitebuilder


@pytest.fixture(scope='function')
def s3_config(request):

    def _remove_env():
        for k, v in settings.items():
            del os.environ[k]

    request.addfinalizer(_remove_env)

    settings = dict(
        AWS_ACCESS_KEY_ID='foo',
        AWS_SECRET_ACCESS_KEY='bar',
        S3_BUCKET='example.com'
    )

    for k, v in settings.items():
        os.environ[k] = v

    return settings


@pytest.fixture(scope='function')
def tmp_build(tmpdir_factory):
    wd = tmpdir_factory.mktemp('build')
    return wd


@pytest.fixture(scope='function')
def creates_posts(request, tmp_pages):
    expected = {'this-post-is-published.md', 'this-post-is-a-draft.md'}

    def _reset_posts():
        for p in tmp_pages.visit():
            if p.basename not in expected:
                p.remove()
    request.addfinalizer(_reset_posts)


@pytest.fixture(scope='function')
def tmp_pages(tmpdir_factory, page_template, draft_post, published_post):
    now = datetime.now()
    wd = tmpdir_factory.mktemp('pages')
    published = wd.ensure('this-post-is-published.md')
    published.write(published_post)
    draft = wd.ensure('this-post-is-a-draft.md')
    draft.write(draft_post)
    return wd


@pytest.fixture(scope='function')
def tmp_pages_path(tmp_pages):
    return os.path.join(tmp_pages.dirname, tmp_pages.basename)


@pytest.fixture(scope='function')
def test_conf(request, tmp_pages_path, tmp_build, s3_config):
    main_settings = {
        'DEBUG': True,
        'TESTING': True,
        'FLATPAGES_ROOT': tmp_pages_path,
        'FLATPAGES_EXTENSION': '.md',
        'FLATPAGES_MARKDOWN_EXTENSIONS': [
            'fenced_code', 'footnotes', 'codehilite'
        ],
        'FLATPAGES_AUTO_RELOAD': True,
        'FREEZER_DESTINATION': tmp_build.strpath
    }
    main_settings.update(s3_config)
    return main_settings


@pytest.fixture(scope='function')
def test_app(request, test_conf):
    app = create_app(test_conf)
    directories = []
    for directory in ('js', 'css'):
        full_path = os.path.join(app.static_folder, directory)
        if not os.path.exists(full_path):
            os.makedirs(full_path)
            directories.append(full_path)
            if directory == 'js':
                filename = os.path.join(full_path, 'app.js')
            else:
                filename = os.path.join(full_path, 'style.css')

            if not os.path.exists(filename):
                with open(os.path.join(full_path, filename), 'w') as f:
                    f.write(filename)

    def _cleanup():
        for d in directories:
            shutil.rmtree(d)

    request.addfinalizer(_cleanup)

    return app


@pytest.fixture(scope='function')
def test_build(test_app):
    sitebuilder.build(test_app)


@pytest.fixture(scope='function')
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
def post_date():
    return datetime(2000, 1, 1)


@pytest.fixture(scope='session')
def published_post(page_template, post_date):
    template = dict(
            title='This Post Exists',
            date_=post_date.strftime('%Y-%m-%d'),
            published=True,
            type_='post',
            tags=','.join(['foo', 'bar', 'baz']),
            content='# Hello! This is a published post'
            )

    return page_template.format(**template)


@pytest.fixture(scope='session')
def draft_post(page_template, post_date):
    template = dict(
            title='This Post Exists',
            date_=post_date.strftime('%Y-%m-%d'),
            published=False,
            type_='post',
            tags=','.join(['fizz', 'buzz', 'foo']),
            content='# Hello! This is a draft post'
            )

    return page_template.format(**template)
