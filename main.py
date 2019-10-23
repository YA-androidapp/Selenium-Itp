#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2019 YA-androidapp(https://github.com/YA-androidapp) All rights reserved.

# Require:
#  $ pip install bs4 lxml selenium selenium-requests

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from seleniumrequests import Firefox
import codecs
import datetime
import os
import re
import requests
import time
import urllib.parse
import urllib.request


currentdirectory = os.getcwd() # os.path.dirname(os.path.abspath(__file__))
os.chdir(currentdirectory)
print(os.getcwd())


# 定数
DATA_FILEPATH = os.path.join(
    currentdirectory, 'dat_'+datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '.txt')
LOG_FILEPATH = os.path.join(
    currentdirectory, 'log_'+datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '.txt')


SHOPS_PER_PAGE = 50
WAITING_TIME = 10000

# URI
baseUri =  'https://itp.ne.jp'
targetUri = 'https://itp.ne.jp/tokyo/genre_dir/475/?ngr=1&sr=1&evdc=1&num=50'


# スクショ保存時のファイル名を生成
def get_filepath():
    now = datetime.datetime.now()
    filename = 'screen_{0:%Y%m%d%H%M%S}.png'.format(now)
    filepath = os.path.join(currentdirectory, filename)
    return filepath


def clickClassName(fox, className):
    fox.find_element_by_class_name(className).click()


def clickId(fox, id):
    fox.find_element_by_id(id).click()


def clickLink(fox, text):
    fox.find_element_by_link_text(text).click()


def clickName(fox, name):
    fox.find_element_by_name(name).click()


def clickSelector(fox, selector):
    fox.find_element_by_css_selector(selector).click()


def clickXpath(fox, xpath):
    fox.find_element_by_xpath(xpath).click()


def clearAndSendKeys(fox, name, text):
    fox.find_element_by_name(name).clear()
    fox.find_element_by_name(name).send_keys(text)


def getFilename(url):
    basename = os.path.basename(str(url))
    basename = basename.split('?')[0] if ('?' in basename) else basename
    return basename


def collect():
    with open(DATA_FILEPATH, 'a', encoding='utf-8') as datafile, open(LOG_FILEPATH, 'a', encoding='utf-8') as logfile:
        print('Start: {}'.format(
            datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')), file=logfile, flush=True)
        binary = FirefoxBinary(
            'C:\\Program Files\\Mozilla Firefox\\firefox.exe')
        profile = FirefoxProfile(
            'C:\\Users\\y\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\hqterean.default')
        fox = webdriver.Firefox(firefox_profile=profile, firefox_binary=binary,
                                executable_path='C:\\geckodriver\\geckodriver.exe')
        fox.set_page_load_timeout(6000)
        try:
            fox.set_window_size(1280, 720)

            print('\tbaseUri: {} {}'.format(
                baseUri, datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')), file=logfile, flush=True)
            print('\ttargetUri: {} {}'.format(
                targetUri, datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')), file=logfile, flush=True)

            fox.get(targetUri)

            # 検索結果1ページ目
            time.sleep(1)
            WebDriverWait(fox, WAITING_TIME).until(
                EC.presence_of_element_located((By.XPATH, '//body')))
            print('body', file=logfile, flush=True)

            source = fox.page_source
            bs = BeautifulSoup(source, 'lxml')
            print('bs', file=logfile, flush=True)
            # print(source, file=logfile, flush=True)

            shops_total = bs.find_all(
                'h1', class_=re.compile('searchResultHeader'))
            if len(shops_total) == 0:
                return
            count_all = int(re.sub('\\D', '', shops_total[0].text))
            last_page = -((-1 * count_all) // SHOPS_PER_PAGE)  # 切り上げ

            i = 0
            for i in range(last_page):
                print('\tpage: {} {} {} {}'.format(
                    i, last_page, count_all, datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')), file=logfile, flush=True)
                tables = bs.find_all(
                    'div', class_=re.compile('searchResultsWrapper'))
                if len(tables) > 0:
                    trs = tables[0].find_all('div', class_=re.compile('normalResultsBox'))
                    if len(trs) > 0:
                        for tr in trs:
                            name = ''
                            address = ''

                            try:
                                # 店
                                h4s = tr.find_all('h4')
                                if len(h4s) > 0:
                                    h4 = h4s[0]
                                    name = str(h4.text).strip()
                                    addresses = tr.find_all('span', class_=re.compile('inlineSmallHeader'))
                                    if len(addresses) > 0:
                                        address = addresses[0].parent
                                        address = ((address.text.split('\u3000')[1]).split(' 地図・ナビ')[0]).strip()

                                    # データファイルに出力
                                    print('{}\t\t{}'.format(name, address),
                                            file=datafile, flush=True)

                            except Exception as e:
                                print(e, file=logfile, flush=True)

                # 次のページに行く
                try:
                    clickLink(fox, '次へ')

                    time.sleep(1)
                    WebDriverWait(fox, WAITING_TIME).until(
                        EC.presence_of_element_located((By.XPATH, '//body')))
                    print('body', file=logfile, flush=True)

                    source = fox.page_source
                    bs = BeautifulSoup(source, 'lxml')
                    print('bs', file=logfile, flush=True)
                except:
                    break

        except Exception as e:
            print(e, file=logfile, flush=True)
        finally:
            # 終了時の後片付け
            try:
                fox.close()
                fox.quit()
                print('Done: {}'.format(
                    datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')), file=logfile, flush=True)
            except:
                pass


if __name__ == '__main__':
    names = collect()
