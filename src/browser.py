# -*- coding: utf-8 -*-

import os
import random
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from time import sleep

from src.constants import TMP_DOWNLOAD_PATH

root_path = os.getcwd()
download_path = os.path.join(root_path, TMP_DOWNLOAD_PATH)

class Browser:
    def __init__(self, has_screen):
        driver_path = os.path.join(root_path, "bin", "geckodriver")

        profile = webdriver.FirefoxProfile()
        profile.set_preference("browser.download.folderList", 2)
        profile.set_preference("browser.download.manager.showWhenStarting", False)
        profile.set_preference("browser.download.dir", download_path)
        profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "video/MP2T;application/vnd.apple.mpegurl")

        options = webdriver.FirefoxOptions()
        if not has_screen:
            options.add_argument("--headless")

        self.driver = webdriver.Firefox(
            executable_path=driver_path, 
            firefox_profile=profile, 
            firefox_options=options)

        self.driver.implicitly_wait(5)

    @property
    def page_height(self):
        return self.driver.execute_script("return document.body.scrollHeight")

    def get(self, url):
        self.driver.get(url)

    def get_new_page(self, url):
        self.driver.execute_script('window.open("{}")'.format(url))

    def get_page_source(self):
        return self.driver.page_source

    @property
    def current_url(self):
        return self.driver.current_url

    def implicitly_wait(self, t):
        self.driver.implicitly_wait(t)

    def find_one(self, css_selector, elem=None, waittime=0):
        obj = elem or self.driver

        if waittime:
            WebDriverWait(obj, waittime).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))
            )

        try:
            return obj.find_element(By.CSS_SELECTOR, css_selector)
        except NoSuchElementException:
            return None

    def find(self, css_selector, elem=None, waittime=0):
        obj = elem or self.driver

        try:
            if waittime:
                WebDriverWait(obj, waittime).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))
                )
        except TimeoutException:
            return None

        try:
            return obj.find_elements(By.CSS_SELECTOR, css_selector)
        except NoSuchElementException:
            return None

    def scroll_down(self, wait=0.3):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        self.randmized_sleep(wait)

    def scroll_up(self, offset=-1, wait=2):
        if offset == -1:
            self.driver.execute_script("window.scrollTo(0, 0)")
        else:
            self.driver.execute_script("window.scrollBy(0, -%s)" % offset)
        self.randmized_sleep(wait)

    def js_click(self, elem):
        self.driver.execute_script("arguments[0].click();", elem)

    def open_new_tab(self, url):
        self.driver.execute_script("window.open('%s');" % url)
        self.driver.switch_to.window(self.driver.window_handles[1])

    def close_new_tab(self):
        self.driver.switch_to.window(self.driver.window_handles[1])
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])

    def close_current_tab(self):
        self.driver.close()

        self.driver.switch_to.window(self.driver.window_handles[0])

    def randmized_sleep(self, average=1):
        _min, _max = average * 1 / 2, average * 3 / 2
        sleep(random.uniform(_min, _max))

    def __del__(self):
        try:
            self.driver.quit()
        except Exception:
            pass
