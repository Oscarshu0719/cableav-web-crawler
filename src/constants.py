# -*- coding: UTF-8 -*-

URL_ROOT = 'https://cableav.tv/{}/'
URL_SUBSTR = 'CLS-{}-v1-a1.ts?'
PATTERN_POST = r'^https://cableav.tv/(?!playlist)([a-zA-Z0-9]+)/.*'
PATTERN_M3U8 = r'(.*)index\.m3u8.*?\&(.*)'
PATTERN_M3U8_URL = r'^CLS-(\d+)-v1-a1\.ts?.*'
PATTERN_URL = r'.*\"single_media_sources\":(\[\{.*\}\])'
PATTERN_BOOKMARK = r"<DT><A HREF=\"(https://cableav.tv/(?!playlist)([a-zA-Z0-9]+)/.*?)\".*<\/A>"

DOWNLOAD_PATH = 'result'
TMP_DOWNLOAD_PATH = 'tmp'
LOG_PATH = 'err.log'
BOOKMARK_PATH = 'bookmark.txt'
INVALID_CHAR = {'\\', '/', ':', '*', '?', '"', '<', '>', '|'}

HAS_SCREEN = False
TIMEOUT = 10
CONVERT_TO_MP4 = True
