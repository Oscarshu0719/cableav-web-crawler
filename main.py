# -*- coding: UTF-8 -*-


from bs4 import BeautifulSoup
from datetime import datetime
from os import getcwd, listdir, makedirs, remove, rmdir, walk
from os.path import exists, join
import re
import requests
import sys
from time import sleep
from tqdm import tqdm

"""
    Disable warning.
"""
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

from src.browser import Browser
from src.constants import *

"""
    Usage:
        python main.py *urls_file*
    
    Args:
        *urls_file*: URLs input path (a file including one URL per line).

    Notice:
        Put chromedriver[.exe] in folder /bin.
"""

tmp_download_path = join(getcwd(), TMP_DOWNLOAD_PATH)
download_path = join(getcwd(), DOWNLOAD_PATH)

def load_urls(path):
    urls = list()

    with open(path, 'r') as file:
        for url in file.readlines():
            m = re.match(PATTERN_POST, url)
            urls.append(URL_ROOT.format(m.group(1)))

    return urls

def clean_tmp_dir(dir):
    for root, dirs, files in walk(dir, topdown=False):
        for name in files:
            remove(join(root, name))
        for name in dirs:
            rmdir(join(root, name))

def concatenate_ts_files(no, output_name, input_dir=tmp_download_path, output_dir=download_path, convert_to_mp4=False):
    output_fullname = join(output_dir, output_name + '.ts')
    with open(output_fullname, "wb+") as file:
        for i in range(1, no + 1):
            filename = join(input_dir, URL_SUBSTR.format(i)[: -1])
            file.write(open(filename, "rb").read())

    clean_tmp_dir(tmp_download_path)

    if convert_to_mp4:
        import subprocess
        command = [
            'ffmpeg', '-y', '-i', output_fullname, join(output_dir, output_name + '.mp4')
        ]
        ffmpeg = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        ffmpeg.communicate()
        remove(output_fullname)

        output_fullname = join(output_dir, output_name + '.mp4')

    print('\n{} - [INFO]: Saved the result file at {}.'.format(
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"), output_fullname))

def download_ts_files(url_root, urls, url_query, output_dir=tmp_download_path):
    cnt_failed = 0
    len_urls = len(urls)
    for i in tqdm(range(len_urls), desc='Downloading ts files'):
        failed = False
        url = url_root + urls[i] + url_query
        browser.get_new_page(url)
        tot_sec = sec = 2
        sleep(sec)
        not_completed = True
        while not_completed: 
            not_completed = False
            for file in listdir(output_dir):
                if '.part' in file:
                    sec += 1
                    sleep(sec)
                    tot_sec += sec
                    not_completed = True
                    if tot_sec > TIMEOUT:
                        msg = '\n{} - [WARN]: Failed to download {}.'.format(
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S"), url)
                        print(msg)
                        with open(LOG_PATH, 'a') as file:
                            file.write(msg[1: ] + '\n')
                        cnt_failed += 1
                        failed = True
                    break
            if failed:
                break
    
    return len_urls - cnt_failed

def parse_m3u8(m3u8, tmp_dir=tmp_download_path):
    match = re.match(PATTERN_M3U8, m3u8)
    if match:
        url_root = match.group(1)
        url_query = match.group(2)
        browser.get_new_page(m3u8)
        
        tot_sec = sec = 1
        sleep(sec)

        while True:
            if 'index.m3u8' not in listdir(tmp_dir):
                sec += 1
                sleep(sec)
                tot_sec += sec
                if tot_sec > TIMEOUT:
                    print('\n{} - [ERR]: Failed to get index.m3u8.'.format(
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                    return [None, None, None]
            else:
                break
                
        m3u8_path = join(tmp_dir, 'index.m3u8')
        with open(m3u8_path, 'r') as file:
            m3u8 = file.readlines()
            no = -1
            for line in m3u8[::-1]:
                match = re.match(PATTERN_M3U8_URL, line)
                if match:
                    no = int(match.group(1))
                    break

            if no < 0:
                print('\n{} - [ERR]: Failed to find the number of M3U8 files.'.format(
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                return [None, None, None]
            
        return [url_root, [URL_SUBSTR.format(i) for i in range(1, no + 1)], url_query]
    else:
        print('\n{} - [ERR]: Failed to parse the root url from {}.'.format(
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"), m3u8))
        return [None, None, None]

def web_crawler(urls_file):
    urls = load_urls(urls_file)

    for i in range(len(urls)):
        print("\n{} - [INFO]: Start downloading video \'{}\'. (Overall progress: {}/{})".format(
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"), urls[i], (i + 1), len(urls)))

        html = requests.get(urls[i]).text
        soup = BeautifulSoup(html, 'lxml')

        m3u8 = soup.find("meta", {"property": "og:video:url"})["content"]
        video_tags = soup.find_all("meta", {"property": "video:tag"})
        best_quality = max([int(tag["content"][: -1]) for tag in video_tags])
        title = soup.find("title").text

        for line in html.split('\n'):
            match = re.match(PATTERN_URL, line)
            if match:
                quality_lists = eval(match.group(1))
                for quality in quality_lists:
                    if str(best_quality) in quality['source_label']:
                        m3u8 = quality['source_file'].replace('\/', '/')
                        break

        print('\n{} - [INFO]: Found: {}. Best quality: {}p, (URL: {}).'.format(
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"), title, best_quality, m3u8))

        [url_root, m3u8_urls, url_query] = parse_m3u8(m3u8)
        if url_root and m3u8_urls and url_query:
            completed = download_ts_files(url_root, m3u8_urls, url_query)
            
            diff = len(m3u8_urls) - completed
            print('\n{} - [INFO]: Total: {}. Completed: {}, failed: {}.'.format(
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"), len(m3u8_urls), completed, diff))
            if diff == 0:
                filename = ''.join(char for char in title if char not in INVALID_CHAR)

                print('\n{} - [INFO]: Start concantenating ts files.'.format(
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                concatenate_ts_files(
                    no=len(m3u8_urls), 
                    output_name=filename,
                    output_dir=download_path,
                    convert_to_mp4=CONVERT_TO_MP4)
            else:
                print('\n{} - [WARN]: Stop concantenating ts files.'.format(
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        else:
            print('\n{} - [WARN]: Failed to download \'{}\'.'.format(
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"), urls[i]))

if __name__ == '__main__':
    assert len(sys.argv) == 2, '\n{} - [ERR]: 2 args (including filename) are needed, but {} given.'.format(
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"), len(sys.argv))
    urls_file = sys.argv[1]

    if not exists(TMP_DOWNLOAD_PATH):
        makedirs(TMP_DOWNLOAD_PATH)
    else:
        clean_tmp_dir(TMP_DOWNLOAD_PATH)

    if not exists(DOWNLOAD_PATH):
        makedirs(DOWNLOAD_PATH)

    browser = Browser(HAS_SCREEN)
    web_crawler(urls_file)
