# -*- coding: UTF-8 -*-

import re

from constants import BOOKMARK_PATH, PATTERN_BOOKMARK

"""
    Usage:
        python bookmark_parser.py *path*
    
    Args:
        *path*: Chrome bookmark file.

    Notice:
        Export bookmarks from 'Bookmark manager'.
"""

def get_urls_from_html(path):
    with open(path, 'r', encoding='utf8') as file:
        html = file.readlines()
        pattern = re.compile(PATTERN_BOOKMARK)

        urls = list()
        for line in html:
            match = pattern.match(line.strip())
            if match:
                urls.append(match.group(1))

    with open(BOOKMARK_PATH, 'w') as file:
        bookmarks = '\n'.join(urls)
        file.write(bookmarks)


if __name__ == '__main__':
    import sys
    assert len(sys.argv) == 2, 'Error: The number of arguments is incorrect.'

    path = sys.argv[1]
    get_urls_from_html(path)
