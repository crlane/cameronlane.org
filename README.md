# cameronlane.org
[![Build Status](https://travis-ci.org/crlane/cameronlane.org.svg)](https://travis-ci.org/crlane/cameronlane.org) [![Coverage Status](https://coveralls.io/repos/crlane/cameronlane.org/badge.svg?branch=master&service=github)](https://coveralls.io/github/crlane/cameronlane.org?branch=master)

This is the code used to write, build, test, and deploy my [personal website and blog](https://cameronlane.org/). The code was originally based on a great blog post by @n1ko, but has since diverged from that project quite a bit. If you're looking for his work, you can check that out <https://nicolas.perriault.net/code/2012/dead-easy-yet-powerful-static-website-generator-with-flask/>. Notable changes from his version: the use of docopt, testing, and python packaging for installation of the sitebuilder script. The javascript and visual design of the site are still almost exactly his. 

In the spirit of his generosity and in the hopes it might be useful to others, I'm open sourcing my version of it as well. 

## Description

This repo is a static website builder/generator implemented in [Python](http://python.org/) using the following tools:

* [Flask](http://flask.pocoo.org/)
* [Frozen-Flask](http://packages.python.org/Frozen-Flask/).
* [docopt](http://docopt.org/)
* [pytest](http://pytest.org/latest/)
* [boto](https://github.com/boto/boto)

## Installation

Note: you need a working installation of Python and [pip](http://pypi.python.org/pypi/pip). I've recreated the sitebuilder script as a python package, so you can install it in your virtualenv. 

```bash
    $ git clone git@github.com/crlane/cameronlane.org.git blog
    $ cd blog
    $ git submodule update --init --recursive 
    $ virtualenv --no-site-packages `pwd`/env
    $ source env/bin/activate
    (env)$ pip install -r requirements.txt
    $ pip install -e .
```
That'll get you up and running. Use `sitebuilder -h` from the command line for options.

## Deploying

I've customized deployment steps to push directly to an s3 bucket configured to serve my site. It works for me, but YMMV. This area of the code is probably the least generalizable section, so caveat emptor. 

Also, see the [License section](#license) of this document for more information about contents copyright.

## Usage

The `sitebuilder` command is installed in the package and is the entry point into the entire system

To serve the website locally (optionally in `DEBUG=True` mode):

    $ sitebuilder serve --debug
    * Running on http://127.0.0.1:8000/
    * Restarting with reloader

This is useful when you want to see changes without having to rebuild the whole site.

To build the static website:

    $ sitebuilder build

Generated HTML files and assets will go to the `./build/` directory.

To deploy the website 

    $ sitebuilder deploy

There's also a command for creating a post:

    $ sitebuilder new --title="My title"
    $ Created pages/drafts/my-title.md
    $ cat pages/drafts/my-title.md
    title: My title
    date: 2013-04-22
    published: False
    type: post
    tags:

## License

Contents in `./pages` (blog posts) are licensed under the terms of the [Creative Commons BY-NC-SA license](http://creativecommons.org/licenses/by-nc-sa/3.0/).

All the rest including Python code, templates, CSS & JavaScript is released under the terms of the [WTFPL](http://sam.zoy.org/wtfpl/).

- This code won't be maintained for any purpose other than my own needs.

## TODO:

* [ ] Dockerize
* [ ] Post travis CI deployment
* [ ] Custom exception types
* [ ] Remove bare print statements
* [ ] Increase coverage
* [ ] Double included static directory included in `freezer.all_urls()`
* [ ] Get build to skip things that aren't needed (unminifed css/js)
* [ ] Clean up assets, get .styl build working.
* [ ] Change layout so article pane is more of the screen (move sidebar left)
* [ ] Coffeescript?
