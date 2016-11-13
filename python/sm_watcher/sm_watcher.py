#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Usage: ./prog board_name keyword
# By default, it will show all articles at the couponslife board of newsmth
# Maintained at
# https://github.com/yeasy/code_snippet/blob/master/python/sm_watcher.py

import random
import re
import signal
import sys
import threading
import time
import datetime
import pickle
from bs4 import BeautifulSoup

import requests

headers_pool = [
    {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US;'
                   'rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'},
    {'User-Agent': 'Mozilla/5.0 (compatible;MSIE 9.0; Windows NT 6.1;'
                   'Trident/5.0)'},
    {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US;) '
                   'AppleWebKit/534.50(KHTML, like Gecko) Version/5.1;'
                   'Safari/534.50'},
    {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) '
                   'AppleWebKit/537.36 (KHTML, like Gecko) '
                   'Chrome/39.0.2171.95 Safari/537.36',
     }
]

DEFAULT_BOARD = 'CouponsLife'
DEFAULT_KEYWORD = ".*"
DEFAULT_URL = "http://www.newsmth.net/bbsdoc.php?board=%s&ftype=6" % \
              DEFAULT_BOARD
DEFAULT_PREFIX = "http://www.newsmth.net/bbstcon.php?board=%s&gid=" % \
                 DEFAULT_BOARD

DB_FILE='/tmp/sm_watcher.data'


def get_time_str(ticks=None, str_format='%H:%M:%S'):
    """
    Get the time string of given ticks or now
    :param ticks: ticks to convert
    :param str_format: Output based on the str_format
    :return:
    """
    t = ticks or time.time()
    return time.strftime(str_format, time.localtime(t))


class BoardWatcher(threading.Thread, object):
    """
    Watcher for a given board, will keep printing new articles with keyword.
    This class is easily implemented based on Threading.Thread or
    Multiprocessing.Process, but now it seems not necessary.
    """

    def __init__(self, board_name=DEFAULT_BOARD, title_keyword=DEFAULT_KEYWORD):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.board = board_name
        self.keyword = title_keyword
        self.url = DEFAULT_URL.replace(DEFAULT_BOARD, self.board)
        self.ct_prefix = DEFAULT_PREFIX.replace(DEFAULT_BOARD, self.board)

        self.max_items = 20
        self.db_file = DB_FILE
        self.db = {}

    def run(self):
        print('board=%s, keyword=%s' % (self.board, self.keyword))
        print("###### start at ", get_time_str(str_format='%Y-%m-%d %H:%M:%S'))
        last_gid = 0
        while True:
            now = datetime.datetime.now()
            entries_new = []
            if datetime.time(1, 0) <= now.time() <= datetime.time(5, 55):
                time.sleep(300)
            else:
                entries_new = self.get_board()
            if entries_new:
                print('Get new entries')
                self.db.update(entries_new)
                gids = sorted(self.db.keys())
                if len(gids) > self.max_items:
                    num_remove = len(gids) - self.max_items
                    for gid in gids[:num_remove]:
                        del self.db[gid]
                self.print_out()
                self.save_out()
            time.sleep(random.uniform(2, 10))

    def get_board(self):
        """ Get articles collection on board.

        Currently we only get the content on latest page

        :return: {
        'xxx': {'gid':xxx,
        'uid': uuu,
        'ts': ttt,
        'title': yyy
        },
        ,...} or {}
        """
        if not self.board:
            return
        page = self.get_page()
        if not page:
            return []
        else:
            return self.parse(page)

    def get_page(self):
        """ Get the page content of given url.

        :return: raw page content or None
        """
        if not self.url:
            return None
        headers = headers_pool[random.randint(0, len(headers_pool)-1)]
        try:
            r = requests.get(self.url, headers=headers, timeout=10)
            r.encoding = r.apparent_encoding

            if r.status_code != requests.codes.ok:
                print('return status code {} is not OK.'.format(r.status_code))
                return None
            return r.text
        except Exception:
            return None

    def parse(self, page):
        """Parse a page into related content

        :param page: raw html page
        :return: {
        'xxx': {'gid':xxx,
        'uid': uuu,
        'ts': ttt,
        'title': yyy
        },
        ,...}
        """
        now = time.time()
        result = {}
        pat = re.compile(u"c.o\(.*?\);", re.UNICODE)
        soup = BeautifulSoup(page, "lxml")

        content = soup.body.text
        #content = content.decode('gb18030', 'ignore')
        entries = re.findall(pat, content)
        for e in entries:
            f = e.split(',')
            ts, title, uid, gid = int(f[4]), f[5], f[2], f[1]
            title, uid = title.strip("' "), uid.strip("' ")
            if uid != 'deliver' and uid != 'SYSOP' \
                    and now - ts < 7200:  # only  in recent two hours
                if self.keyword and re.search(self.keyword, title):
                    result[gid] = {
                        'gid': gid,
                        'user_name': uid,
                        'ts': get_time_str(ts),
                        'title': title,
                        'url': self.ct_prefix+gid,
                    }
        return result

    def print_out(self):
        """
        Out put the interested entries: ts, title, uid, gid
        :return:
        """
        for gid in self.db:
            item = self.db[gid]
            print('gid={}, ts={}, user_name={}, title={}'.format(
                gid, item['ts'], item['user_name'], item['title']))

    def save_out(self):
        """Save into db

        :return:
        """
        if not self.db or not self.db_file:
            print('No db file to save out')
            return

        pickle.dump(self.db, open(self.db_file, 'wb'))


def signal_handler(signal_num, frame):
    print('You pressed Ctrl+C!')
    sys.exit(0)

if __name__ == "__main__":
    board, keyword = DEFAULT_BOARD, DEFAULT_KEYWORD
    if len(sys.argv) == 2:
        board = DEFAULT_BOARD
    elif len(sys.argv) == 3:
        board, keyword = sys.argv[1], sys.argv[2]

    signal.signal(signal.SIGINT, signal_handler)

    p = BoardWatcher(board, keyword)
    p.start()

    while True:
        time.sleep(1)