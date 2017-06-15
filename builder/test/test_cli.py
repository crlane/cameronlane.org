import os
import pytest
import subprocess

from unittest.mock import patch, Mock

from builder.cli import sitebuilder
from builder.app import get_pages

COMMANDS = ['build', 'serve', 'deploy', 'new']


@pytest.fixture(scope='function', params=COMMANDS)
def mock_args(request):
    command_args = {cmd: True if request.param == cmd else False for cmd in COMMANDS}
    if request.param == 'new':
        command_args['TITLE'] = 'this-is-a-new-post'
    return request.param, command_args


@pytest.mark.usefixtures('creates_posts')
def test_new_blog_post_uses_title(test_app, tmp_pages):
    expected_title = 'This is a new post'
    assert len(tmp_pages.join('posts').listdir()) == 2
    sitebuilder.new(test_app, title=expected_title)
    with test_app.test_request_context():
        pages = get_pages()
        pages.reload()
        assert len([p for p in pages if p.meta.get('type') == 'post']) == 3
        # most recent first
        post = pages.get('posts/this-is-a-new-post')
        assert post is not None
        assert post.meta.get('title') == expected_title


@pytest.mark.usefixtures('creates_posts')
def test_new_blog_post_creates_default_file(test_app, tmp_pages):
    assert len(tmp_pages.join('posts').listdir()) == 2
    sitebuilder.new(test_app)
    assert len(tmp_pages.join('posts').listdir()) == 3


def test_cli_calls_correct_function(test_app, mock_args):
    command, _args = mock_args
    create = Mock(return_value=test_app)
    arguments = Mock(return_value=_args)
    with patch.object(sitebuilder, 'create_app', create):
        with patch.object(sitebuilder, 'docopt', arguments):
            with patch.object(sitebuilder, command):
                sitebuilder.main()
                assert getattr(sitebuilder, command).call_count == 1


def test_cli_deploy_calls_build(test_app, s3_config):
    with patch.object(sitebuilder, 'build'):
        with patch.object(sitebuilder, 'S3Connection'):
            sitebuilder.deploy(test_app)
        assert sitebuilder.build.call_count == 1


def test_get_files_ignores_hidden_things(tmp_build, test_build):
    files = sitebuilder._get_files_for_deploy(tmp_build.strpath)
    assert files
    assert not any(keyname.startswith('.') for keyname, localpath in files)


def test_get_files_ignores_javascripts(tmp_build, test_build):
    # if debug is not on
    files = sitebuilder._get_files_for_deploy(tmp_build.strpath)
    assert files
    assert not any('javascripts' in keyname for keyname, localpath in files)


def test_get_files_ignores_stylesheets(tmp_build, test_build):
    # if debug is not on
    files = sitebuilder._get_files_for_deploy(tmp_build.strpath)
    assert files
    assert not any('stylesheets' in keyname for keyname, localpath in files)
