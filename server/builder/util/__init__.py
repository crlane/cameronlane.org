import re
import os

from unicodedata import normalize

PUNCT_RE = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')


def slugify(text, delim=u'-'):
    '''Generates an slightly worse ASCII-only slug.'''
    result = []
    for word in PUNCT_RE.split(text.lower()):
        word = normalize('NFKD', word)
        if word:
            result.append(word)
    return delim.join(result)


def get_file_path(app, pathargs):
    return os.path.join(os.path.abspath(app.config['FLATPAGES_ROOT']), *pathargs)
