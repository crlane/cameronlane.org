import json
import logging

from collections import Counter
from flask import (
    Flask,
    Blueprint,
    current_app,
    render_template,
    url_for
)

from flask_flatpages import FlatPages
from flask_frozen import Freezer
from flask_assets import (
    Environment,
    Bundle
)

from urllib import unquote
from datetime import date, datetime

log = logging.getLogger(__name__)


blog = Blueprint('blog', __name__, static_folder='static', template_folder='templates')
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
    register_errorhandlers(app)

    # create the static assets
    create_assets(app)

    # get the flat pages
    get_pages().init_app(app)
    return app


def create_freezer(app):
    freezer = Freezer(app)
    return freezer


# Blueprints cannot register 500 error handler see
# http://stackoverflow.com/questions/30108000/flask-register-blueprint-error-python
def register_errorhandlers(app):
    def render_error(error):
        error_code = getattr(error, 'code', 500)
        return render_template("{0}.html".format(error_code)), error_code

    for errcode in [403, 404, 500]:
        app.errorhandler(errcode)(render_error)
    return None


def create_assets(app):
    js_filters = ['jsmin'] if not app.debug else []
    js = Bundle(
        'javascripts/app.js',
        'javascripts/libs/jquery/jquery-1.11.2.js',
        'javascripts/libs/jqcloud/jqcloud-1.0.4.js',
        filters=js_filters,
        output='js/app.js')

    css_filters = ['cssmin', 'stylus'] if not app.debug else []
    css = Bundle(
        'stylesheets/style.css',
        'stylesheets/jqcloud.css',
        'stylesheets/code.css',
        filters=css_filters,
        output='css/style.css')

    # names the assets to be used in templates
    assets = Environment(app)
    assets.register('js_all', js)
    assets.register('css_all', css)
    return assets


@blog.route('/')
def index():
    page = pages.get_or_404('home')
    return render_template('index.html',
                           page=page, section='home', title='index')


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
    posts = pages_filter(year=year)
    return render_template('archives.html',
                           posts=posts, year=year, section='blog',
                           title='archives {}'.format(year))


@blog.route('/blog/<path:path>/')
def page(path):
    post = pages.get_or_404(path)
    return render_template('post.html',
                           post=post, section='blog',
                           title=post.meta.get('title'))


@blog.route('/blog/tag/')
def tags():
    tags = get_tag_counts(pages_filter())
    tag_array = list(generate_tag_wordcloud_data(tags))
    return render_template('tagcloud.html',
                           tags=json.dumps(tag_array),
                           section='blog', title='tagcloud')


@blog.route('/blog/tag/<string:tag>/')
def tag(tag):
    tag = unquote(tag)
    tagged = pages_filter(tag=tag)
    return render_template('tag.html',
                           pages=tagged, tag=tag, section='blog', title=tag)


@blog.route('/contact/')
def contact():
    return render_template('contact.html',
                           section='contact', title='Cameron Lane')


@blog.route('/resume/')
def resume():
    page = pages.get_or_404('resume')
    return render_template('resume.html',
                           page=page, section='resume', title='Cameron Lane')


@blog.context_processor
def current_year():
    return dict(current_year=datetime.utcnow().year)


# helpers
def pages_filter(tag=None, year=None):
    '''
    Retrieves pages matching passed criteria.
    '''
    # only posts
    articles = [p for p in pages if p.meta.get('type') == 'post']
    # filter unpublished article
    if not current_app.debug:
        articles = [p for p in articles if p.meta.get('published')]
    # filter tag
    if tag:
        articles = [p for p in articles if tag in p.meta.get('tags', [])]
    # filter year
    if year:
        articles = [p for p in articles if p.meta.get('date').year == year]

    # sort by date
    articles = sorted(articles, reverse=True,
                      key=lambda p: p.meta.get('date', date.today()))

    # assign prev/next page in series
    # for i, article in enumerate(articles):
    #    if i != 0:
    #        if section and articles[i - 1].meta.get('section') == section:
    #            article.prev = articles[i - 1]
    #    if i != len(articles) - 1:
    #        if section and articles[i + 1].meta.get('section') == section:
    #            article.next = articles[i + 1]

    return articles


def paginate(articles, offset=0, limit=0):
    if offset and limit:
        return articles[offset:offset + limit]
    elif limit:
        return articles[:limit]
    elif offset:
        return articles[offset:]
    else:
        return articles


def get_years_data(pages):
    years = list(set([page.meta.get('date').year for page in pages]))
    years.reverse()
    return years


def get_tag_counts(pages):
    tag_dict = Counter()
    for p in pages:
        tags = p.meta.get('tags')
        if tags:
            tag_dict.update([t.strip().lower() for t in tags.split(',') if t])
    return dict(tag_dict)


def generate_tag_wordcloud_data(tags):
    for tag, weight in tags.iteritems():
        yield dict(text=tag, weight=weight, link=url_for('.tag', tag=tag))
