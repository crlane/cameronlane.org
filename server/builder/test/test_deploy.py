import pytest

from unittest.mock import patch

from builder import deploy


@pytest.yield_fixture
def deployment(test_app, test_build):
    with patch.object(deploy.Deployment, 's3'):
        with patch.object(deploy.Deployment, 'cloudfront'):
            yield deploy.Deployment(test_app)


def test_deploy_connection(deployment):
    deployment.deploy(dry_run=True)
    assert deployment.s3.get_bucket.call_count == 1


def test_get_files_returns_non_empty_list(deployment):
    files = deployment.get_files_for_deploy()
    assert [f for f in files]


def test_get_files_ignores_hidden_things(deployment):
    files = deployment.get_files_for_deploy()
    assert not any(keyname.startswith('.') for keyname, localpath in files)
