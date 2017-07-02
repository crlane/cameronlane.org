import os

from urllib.parse import quote

from boto.s3.connection import S3Connection, ProtocolIndependentOrdinaryCallingFormat
from boto.s3.key import Key
from boto.cloudfront import CloudFrontConnection


class ConfigurationError(Exception):
    pass


class Deployment:

    def __init__(self, app, build_dir=None):
        self.app = app
        if not build_dir:
            build_dir = self.app.config['FREEZER_DESTINATION']
        self.build_dir = build_dir
        self._credentials = None
        self._s3 = None
        self._cloudfront = None

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

    def get_files_for_deploy(self):
        for dirpath, dirnames, filenames in os.walk(self.build_dir):
            current = os.path.basename(dirpath)
            # ignore hidden directories
            if current.startswith('.'):
                continue
            # ignore un min/uglifed css and javascripts
            elif 'javascripts' in dirpath or 'stylesheets' in dirpath:
                continue
            for f in filenames:
                # ignore hidden files
                if f.startswith('.'):
                    continue
                local_path = os.path.join(dirpath, f)
                # keyname is relative to the build directory
                # i.e., ~/src/blog/blog/build/foo/bar.html becomes
                # bar/foo.html and src/blog/blog/build/index.html
                # becomes index.html
                keyname = os.path.relpath(local_path, self.build_dir)
                yield keyname, local_path

    def deploy(self, delete=False, dry_run=True):
        try:
            b = self.app.config.get('S3_BUCKET')
            bucket = self.s3.get_bucket(b)
        except Exception as e:
            print('Unable to get s3 bucket {}'.format(b))
            raise

        for key in bucket.list():
            if key.name.startswith('.well-known'):
                print('Skipping DNS verification: {}'.format(key.name))
                continue
            elif key.name.startswith('images'):
                print('Skipping images')
                continue
            elif key.name.endswith('404.html'):
                print('Skipping error page')
                continue

            if delete and not dry_run:
                print('Deleting {}'.format(key.name))
                key.delete()

        for keyname, localpath in self.get_files_for_deploy():
            if not dry_run:
                k = Key(bucket)
                k.key = quote(keyname)
                k.set_contents_from_filename(localpath)
                k.set_acl('public-read')
            print('Set key contents for {}'.format(keyname))

    def invalidate(self, endpoints=None, dry_run=True):
        if endpoints is None:
            endpoints = ['/*']
        cf_id = os.getenv('CLOUDFRONT_ID')
        if cf_id is None:
            print('No distribution id set, skipping invalidation...')
            return
        try:
            if not dry_run:
                resp = self.cloudfront.create_invalidation_request(cf_id, endpoints)
                print('Invalidation response: {}'.format(resp))
            else:
                print('Skipping invalidaiton due to --dry-run flag')
        except Exception as e:
            print('Unable to create invalidation request: {}'.format(e))
        else:
            print('Invalidation request succeeded')
