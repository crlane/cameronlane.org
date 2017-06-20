import os

from urllib.parse import quote

from boto.s3.connection import S3Connection, ProtocolIndependentOrdinaryCallingFormat
from boto.s3.key import Key


class ConfigurationError(Exception):
    pass


class Deployment:

    def __init__(self, app, build_dir=None):
        self.app = app
        if not build_dir:
            build_dir = self.app.config['FREEZER_DESTINATION']
        self.build_dir = build_dir
        self._connect()

    def _connect(self):
        connect = {k.lower(): self.app.config[k] for k in
                   ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY'] if self.app.config.get(k)}
        if not connect:
            connect['profile_name'] = 'blog_deploy'
        calling_format = ProtocolIndependentOrdinaryCallingFormat()
        connect.update({'calling_format': calling_format})
        try:
            conn = S3Connection(**connect)
            bucket = self.app.config.get('S3_BUCKET')
            self.bucket = conn.get_bucket(bucket)
        except Exception as e:
            raise ConfigurationError('unable to connect and find bucket')

    def get_files_for_deploy(self):
        for dirpath, dirnames, filenames in os.walk(self.build_dir):
            current = os.path.basename(dirpath)
            # ignore hidden directories
            if current.startswith('.'):
                continue
            # ignore un min/uglifed js and javascripts
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
        for key in self.bucket.list():
            if key.name.startswith('.well-known'):
                print('Skipping DNS verification: {}'.format(key.name))
                continue
            if delete and not dry_run:
                print('Deleting {}'.format(key.name))
                key.delete()

        for keyname, localpath in self.get_files_for_deploy():
            if not dry_run:
                k = Key(self.bucket)
                k.key = quote(keyname)
                k.set_contents_from_filename(localpath)
            print('Set key contents for {}'.format(keyname))
