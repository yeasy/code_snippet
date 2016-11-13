# coding=utf-8

from bs4 import BeautifulSoup

import os
import random
import requests
import sys
import time

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/39.0.2171.95 Safari/537.36',
    'charset':'utf8'
}


def get_ss(url):
    """Get ss list from given url

    :param url:
    :return: list of ss addrs like ['ss://xxxxxxx','ss://yyyyy']
    """
    r = requests.get(url, headers=headers, timeout=10)

    if r.status_code != requests.codes.ok:
        print('return status code {} is not OK.'.format(r.status_code))
        return None
    r.encoding = r.apparent_encoding
    soup = BeautifulSoup(r.text, "lxml")
    row_heads = soup.body.find_all('td', text='日本樱花')
    rows = map(lambda x: x.find_parent("tr"), row_heads)
    values = map(lambda x: x.find_all('td'), rows)

    proxy_list = []
    for v in values:
        c = map(lambda x: x.text, v)
        lc = list(c)
        proxy = 'ss://{}:{}@{}:{}'.format(lc[4],lc[3],lc[1],lc[2])
        # proxy = ss://rc4-md5:password@ip:port
        proxy_list.append(proxy)
    return proxy_list


def update_cow(ss_list):
    f_rc_bak = open(os.path.expanduser('~')+'/.cow/rc.bak','r').read()
    f_rc = open(os.path.expanduser('~')+'/.cow/rc','w')
    if not f_rc_bak or not f_rc:
        print('Error to open rc_bak or rc files')
        return
    f_rc.write(f_rc_bak)
    f_rc.write('# other ss proxies\n')
    for ss in ss_list:
        f_rc.write('proxy = {}\n'.format(ss))
    os.system('killall -9 cow')
    print('Update!')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('should input an url')
        exit()
    else:
        ss_list_old = []
        check_interval = 300  # how many seconds wait for check, auto-adjust
        while True:
            ss_list = get_ss(sys.argv[1])
            if ss_list and ss_list != ss_list_old: # find new, reduce interval
                print('Get new ss list')
                print('\n'.join(ss_list))
                print('next interval = {}'.format(check_interval))
                update_cow(ss_list)
                ss_list_old = ss_list
                check_interval -= random.randint(0, 10)
                time.sleep(check_interval)
            else:  # duplicated content, we're checking too quick
                next_wait = random.randint(10, 60)
                check_interval += next_wait
                time.sleep(next_wait)
