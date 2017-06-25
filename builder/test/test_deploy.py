import pytest

from unittest.mock import patch

from builder.deploy import Deployment


@pytest.yield_fixture
def deployment(test_app, test_build):
    with patch.object(Deployment, '_connect'):
        yield Deployment(test_app)


def test_connect_is_called_in_constructor(deployment):
    assert deployment._connect.call_count == 1


def test_get_files_returns_non_empty_list(deployment):
    files = deployment.get_files_for_deploy()
    assert [f for f in files]


def test_get_files_ignores_hidden_things(deployment):
    files = deployment.get_files_for_deploy()
    assert not any(keyname.startswith('.') for keyname, localpath in files)


def test_get_files_ignores_javascripts(deployment):
    # if debug is not on
    files = deployment.get_files_for_deploy()
    assert not any('javascripts' in keyname for keyname, localpath in files)


def test_get_files_ignores_stylesheets(deployment):
    # if debug is not on
    files = deployment.get_files_for_deploy()
    assert not any('stylesheets' in keyname for keyname, localpath in files)
