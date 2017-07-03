import pytest

from unittest.mock import patch, DEFAULT

from builder.deploy import Deployment


@pytest.yield_fixture
def deployment(test_app, test_build):
    mocks = {
        's3': DEFAULT,
        'cloudfront': DEFAULT,
    }
    with patch.multiple(Deployment, **mocks):
        yield Deployment(test_app, delete=False, dry_run=True)


def test_deploy_connection_gets_bucket_exactly_once(deployment):
    deployment.deploy()
    assert deployment.s3.get_bucket.call_count == 1
    assert deployment.s3.get_bucket.called_with(deployment.app.config['S3_BUCKET'])


def test_get_files_returns_non_empty_list(deployment):
    files = deployment.get_files_for_deploy()
    assert [f for f in files]


def test_get_files_ignores_hidden_things_except_for_well_known(deployment):
    files = deployment.get_files_for_deploy()
    assert not any(keyname.startswith('.') for keyname, localpath in files if not keyname.startswith('.well-known'))
