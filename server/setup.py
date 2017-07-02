from setuptools import (
    setup,
    find_packages
)

TESTS_REQUIRE = []
INSTALL_REQUIRES = []

with open('requirements.txt', 'r') as f:
    INSTALL_REQUIRES += [l.strip() for l in f.readlines()]

with open('test_requirements.txt', 'r') as f:
    TESTS_REQUIRE += [l.strip() for l in f.readlines()]

setup(
    name='blog-builder',
    version='1.2',
    description='A python app to build, deploy a simple static flask app',
    author='Cameron Lane',
    author_email='crlane@adamanteus.com',
    url='https://github.com/crlane/cameronlane.org',
    packages=find_packages(exclude=['test', 'tests', 'tests.*']),
    zip_safe=False,
    package_data={
        'builder': [
            'pages/*.md',
            'pages/images/*.png',
            'templates/*.html',
            'static/css/*.css',
            'static/favicon.ico',
            'static/js/*.js',
            'static/*.txt',
        ]
    },
    include_package_data=True,
    classifiers=['Private :: Do Not Upload'],
    install_requires=INSTALL_REQUIRES,
    extras_require={
        'testing': TESTS_REQUIRE,
        'development': ['ipython', 'ipdb']
    },
    entry_points={
        'console_scripts': [
            'sitebuilder=builder.cli.sitebuilder:main'
        ],
    },
)
