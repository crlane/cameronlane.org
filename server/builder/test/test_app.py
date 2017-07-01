import pytest

from datetime import datetime
from builder.app import (
    pages_filter,
    get_tag_counts
)


def test_get_home_page(test_client):
    response = test_client.get('/')
    assert response.status_code == 200, 'Bad response for home page'


@pytest.mark.parametrize('page_name', ['blog', 'resume', 'contact'])
def test_get_index_page(test_client, page_name):
    response = test_client.get('/{}/'.format(page_name))
    assert page_name in str(response.get_data())
    assert response.status_code == 200, 'Bad response for {} page'.format(page_name)


@pytest.mark.skip
@pytest.mark.parametrize('error_code', ['404', '403', '500'])
def test_get_error_pages(test_client, test_app, error_code):
    response = test_client.get('/{}.html'.format(error_code))
    assert response.status_code == 200, 'Unable to find error page'


@pytest.mark.parametrize('subpage', ['archives', 'tag'])
def test_get_blog_subpage(test_client, subpage):
    response = test_client.get('/blog/{}/'.format(subpage))
    assert response.status_code == 200, 'Bad response for blog {} page'.format(subpage)


def test_get_archives_year(test_client):
    response = test_client.get('/blog/archives/2015/')
    assert response.status_code == 200, 'Bad response for blog archives of specific year'


def test_get_existing_blog_post(test_client):
    response = test_client.get('/blog/this-post-is-published/')
    assert response.status_code == 200, 'Bad response for existing page'


def test_get_missing_blog_post(test_client):
    response = test_client.get('/blog/this-post-does-not-exist/')
    assert response.status_code == 404, 'Bad response for missing page'


def test_get_existing_tag_index(test_client):
    response = test_client.get('/blog/tag/existing/')
    assert response.status_code == 200, 'Bad response for existing tag index page'


def test_get_missing_tag_index(test_client):
    response = test_client.get('/blog/tag/missing/')
    # even though the tag DNE, we 200 because it's a list of pages containing tag
    # hence, an empty list
    assert response.status_code == 200, 'Bad response for missing tag index page'


def test_pages_filter_by_existing_year(test_app, post_date):
    with test_app.test_request_context():
        expected_count = 1
        year = post_date.year
        assert len(pages_filter(year=year)) == 2,\
            'Incorrect number of posts for existing year, {}'.format(year)


def test_pages_filter_by_missing_year(test_app, post_date):
    with test_app.test_request_context():
        year = post_date.year + 10
        assert len(pages_filter(year=year)) == 0,\
            'Incorrect number of posts for missing year: {}'.format(year)


@pytest.mark.parametrize('debug,tag,pages_count', [
    (True, 'foo', 2), (True, 'bar', 1), (True, 'baz', 1),
    (True, 'fizz', 1), (True, 'buzz', 1), (True, 'notatag', 0),
    (False, 'foo', 1), (False, 'bar', 1), (False, 'baz', 1),
    (False, 'fizz', 0), (False, 'buzz', 0), (False, 'notatag', 0)])
def test_pages_filter_by_tag_based_on_debug(test_app, debug, tag, pages_count):
    test_app.debug = debug
    with test_app.test_request_context():
        pages = pages_filter(tag=tag)
        assert len(pages) == pages_count,\
            'Incorrect tag count for {} with debug={}'.format(tag, debug)
    test_app.debug = True


def test_pages_filter_by_missing_tag_returns_empty(test_app):
    test_app.debug = True
    with test_app.test_request_context():
        assert pages_filter(tag='not present') == []


@pytest.mark.parametrize('debug,pages_count', [(True, 2), (False, 1)])
def test_pages_filter_selects_posts_based_on_debug(request, test_app, debug, pages_count):
    test_app.debug = debug
    with test_app.test_request_context():
        pages = pages_filter()
        assert len(pages) == pages_count, 'Pages count incorrect when debug={}'.format(debug)
    test_app.debug = True


@pytest.mark.parametrize('debug,expected_tags',
        [(True, {'foo': 2, 'bar': 1, 'baz': 1, 'fizz': 1, 'buzz':1}), 
            (False, {'foo': 1, 'bar': 1, 'baz': 1})])
def test_get_tag_counts_based_on_debug(request, test_app, debug, expected_tags):
    test_app.debug = debug
    with test_app.test_request_context():
        tags = get_tag_counts(pages_filter())
        assert tags == expected_tags, 'Tag counts are incorrect'
    test_app.debug = True
