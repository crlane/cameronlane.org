import os
from hashlib import md5

from urllib.parse import quote

from boto.s3.connection import S3Connection, ProtocolIndependentOrdinaryCallingFormat
from boto.s3.key import Key
from boto.cloudfront import CloudFrontConnection


class ConfigurationError(Exception):
    pass


class Deployment:

    def __init__(self, app, build_dir=None, delete=False, dry_run=False):
        self.app = app
        if not build_dir:
            build_dir = self.app.config['FREEZER_DESTINATION']
        self.build_dir = build_dir
        self.delete = delete
        self.dry_run = dry_run

        self._credentials = None
        self._s3 = None
        self._cloudfront = None

        # this will be ignored when cleaning up remote server
        # TODO: make a way to generate 404.html
        self.ignores = {'404.html', '/images'}

    @property
    def s3(self):
        if self._s3 is None:
            calling_format = ProtocolIndependentOrdinaryCallingFormat()
            connection_params = {'calling_format': calling_format}
            connection_params.update(self.credentials)
            try:
                self._s3 = S3Connection(**connection_params)
            except Exception as e:
                msg = 'Error connecting to s3: {}'.format(e)
                print(msg)
                raise ConfigurationError(msg)
        return self._s3

    @property
    def cloudfront(self):
        if self._cloudfront is None:
            try:
                self._cloudfront = CloudFrontConnection(**self.credentials)
            except Exception as e:
                msg = 'Error connecting to cloudfront: {}'.format(e)
                print(msg)
                raise ConfigurationError(msg)
        return self._cloudfront

    @property
    def credentials(self):
        if self._credentials is None:
            self._credentials = {k.lower(): self.app.config[k] for k in
                ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY'] if self.app.config.get(k)}
            if not self._credentials:
                self._credentials['profile_name'] = 'blog_deploy'
        return self._credentials

    def md5(self, filepath):
        with open(filepath, 'rb') as f:
            return md5(f.read()).hexdigest()

    def get_files_for_deploy(self):
        for dirpath, dirnames, filenames in os.walk(self.build_dir):
            current = os.path.basename(dirpath)
            # ignore hidden directories, except for keybase directory
            if current.startswith('.') and current != '.well-known':
                continue
            for f in filenames:
                # ignore hidden files except for the generated .tags
                if f.startswith('.') and f != '.tags':
                    continue
                local_path = os.path.join(dirpath, f)
                # keyname is relative to the build directory
                # i.e., ~/src/blog/blog/build/foo/bar.html becomes
                # bar/foo.html and src/blog/blog/build/index.html
                # becomes index.html
                keyname = os.path.relpath(local_path, self.build_dir)
                yield keyname, local_path

    def _delete(self, remote_key):
        if self.delete and not self.dry_run:
            try:
                remote_key.delete()
                print(f'\tDeleted {remote_key.name}')
            except Exception as e:
                print(f'\tError deleting {remote_key.name}')
        else:
            print(f'\tWill not delete key: {remote_key.name} based dry:{self.dry_run} delete:{self.delete}')

    def _push(self, bucket, keyname, local_path):
        if not self.dry_run:
            k = Key(bucket)
            k.key = quote(keyname)
            k.set_contents_from_filename(local_path, policy='public-read')
            print(f'\tSet key contents for {k.key}')
        else:
            print(f'\tDry run: Would create the key: {keyname}')

    def _same_contents(self, remote_key, local_path):
        return remote_key.etag.strip('"') == self.md5(local_path)

    def _cleanup(self, remote_keys):
        while remote_keys:
            name, extra_key = remote_keys.popitem()
            if name not in self.ignores:
                print(f'Extra remote key: {name}')
                self._delete(extra_key)
            else:
                print(f'Ignoring extra file: {name}')

    def deploy(self):
        try:
            b = self.app.config.get('S3_BUCKET')
            bucket = self.s3.get_bucket(b)
            remote_keys = {k.name: k for k in bucket.get_all_keys()}
        except Exception as e:
            print(f'Unable to get s3 bucket {b}')
            raise

        for keyname, local_path in self.get_files_for_deploy():
            remote_key = remote_keys.pop(keyname, None)
            # remote key must exist and have the same contents as local path,
            # or we delete and upload again
            if not remote_key:
                print(f'Remote key does not exist, pushing: {keyname}')
                self._push(bucket, keyname, local_path)
            elif not self._same_contents(remote_key, local_path):
                print(f'Remote key contents have changed, deleting/pushing: {keyname}')
                self._delete(remote_key)
                self._push(bucket, keyname, local_path)
            else:
                print(f'Remote key has not changed: skipping {remote_key.name}')

        self._cleanup(remote_keys)

    def invalidate(self, endpoints=None):
        if endpoints is None:
            endpoints = ['/*']
        cf_id = os.getenv('CLOUDFRONT_ID')
        if cf_id is None:
            print('No distribution id set, skipping invalidation...')
            return
        try:
            if not self.dry_run:
                resp = self.cloudfront.create_invalidation_request(cf_id, endpoints)
                print(f'Invalidation response: {resp}')
            else:
                print('Skipping invalidaiton due to --dry-run flag')
        except Exception as e:
            print(f'Unable to create invalidation request: {e}')
        else:
            print('Invalidation request succeeded')
