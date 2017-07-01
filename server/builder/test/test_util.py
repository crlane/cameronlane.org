import os
import pytest

from builder.util import (
    get_file_path,
    slugify
)


@pytest.mark.parametrize('title,expected', [
    (u'Hello, World!', 'hello-world'),
    (u'Who\'s #1?', 'who-s-1'),
])
def test_slugify(title, expected):
    assert slugify(title) == expected


def test_get_post_file_path(test_app, tmp_pages, section='foo', title='this-is-a-new-filepath.md'):
    expected = os.path.join(tmp_pages.strpath, section, title)
    assert get_file_path(test_app, [section, title]) == expected, 'File path is not correct'
