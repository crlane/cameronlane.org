import json
import logging

from collections import Counter
from datetime import datetime
from itertools import chain

from urllib.parse import unquote

from flask import (
    abort,
    Blueprint,
    Flask,
    current_app,
    jsonify,
    render_template,
    url_for
)

from flask_flatpages import FlatPages
from flask_frozen import Freezer
from flask_htmlmin import HTMLMIN

from builder.posts import BlogPost

log = logging.getLogger(__name__)


blog = Blueprint(
    'blog', __name__,
    static_folder='static',
    template_folder='templates'
)

pages = None


def get_pages():
    global pages
    if pages is None:
        pages = FlatPages()
    return pages


def create_app(settings=None):
    # create app and configure
    app = Flask(__name__)
    app.config.from_pyfile('config.py')

    if settings is not None:
        app.config.update(settings)

    app.register_blueprint(blog)
    HTMLMIN(app)

    # get the flat pages
    get_pages().init_app(app)

    return app


def create_freezer(app):
    freezer = Freezer(app)
    return freezer


@blog.app_errorhandler(403)
def forbidden(e):
    return render_template('403.html', section='error'), 403


@blog.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html', section='error'), 404


@blog.app_errorhandler(500)
def internal_server_error(e):
    return render_template('500.html', section='error'), 500


@blog.route('/')
def index():
    return render_template('index.html', section='home', title='index')


@blog.route('/blog/')
def blog_posts():
    posts = pages_filter()
    return render_template('blog.html',
                           posts=posts, section='blog', title='posts')


@blog.route('/blog/archives/')
def archives():
    posts = pages_filter()
    years = get_years_data(posts)
    return render_template('archives.html',
                           posts=posts, years=years,
                           section='blog', title='archives')


@blog.route('/blog/archives/<int:year>/')
def archive(year):
    posts = pages_filter(lambda p: p.from_year(year))
    return render_template('archives.html',
                           posts=posts, year=year, section='blog',
                           title='archives {}'.format(year))


@blog.route('/blog/<path:path>/')
def page(path):
    post = BlogPost(pages.get_or_404(path))
    return render_template('post.html',
                           post=post, section='blog',
                           title=post.title)


@blog.route('/.well-known/keybase.txt')
def keybase_verification_file():
    return blog.send_static_file('keybase.txt')


@blog.route('/robots.txt')
def seo_instruction_file():
    return blog.send_static_file('robots.txt')


@blog.route('/blog/tag/')
def tags():
    tag_array = list(generate_tag_wordcloud_data())
    return render_template('tagcloud.html',
                           tags=json.dumps(tag_array),
                           section='blog', title='tagcloud')


@blog.route('/blog/tag/.tags')
def static_tag_cloud_data():
    tag_array = list(generate_tag_wordcloud_data())
    return jsonify(tag_array), {'content-type': 'application/json'}


@blog.route('/blog/tag/<string:tag>/')
def tag(tag):
    tag = unquote(tag)
    tagged_posts = pages_filter(lambda p: p.has_tag(tag))
    if not tagged_posts:
        abort(404)
    return render_template('tag.html',
                           posts=tagged_posts, tag=tag, section='blog', title=tag)


@blog.route('/contact/')
def contact():
    return render_template('contact.html',
                           section='contact', title='Cameron Lane')


@blog.route('/resume/')
def resume():
    return render_template('resume.html',
                           section='resume', title='Cameron Lane')


@blog.context_processor
def current_year():
    return dict(current_year=datetime.utcnow().year)


def pages_filter(*filters):
    '''
    Retrieves pages matching passed criteria.

    :param filters: Function Predicates that must be matched in order for
    the page to be included in output
    '''

    posts = map(BlogPost, pages)

    filters = list(filters)
    if not current_app.debug:
        filters.append(lambda p: p.is_published)

    posts = (p for p in posts if all(f(p) for f in filters))

    # sort by date
    return sorted(posts, reverse=True, key=lambda p: p.date)


def paginate(articles, offset=0, limit=0):
    if offset and limit:
        return articles[offset:offset + limit]
    elif limit:
        return articles[:limit]
    elif offset:
        return articles[offset:]
    else:
        return articles


def get_years_data(posts):
    years = list(set(p.date.year for p in posts))
    years.sort(reverse=True)
    return years


def generate_tag_wordcloud_data():
    tags = Counter(chain.from_iterable(p.tags for p in pages_filter()))
    for tag, weight in tags.items():
        yield dict(text=tag, weight=weight, link=url_for('.tag', tag=tag))
