# coding=utf-8

from bs4 import BeautifulSoup

import os
import random
import requests
import shutil
import sys
import time



headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:12.0) Gecko/20100101 Firefox/12.0',
    'charset':'utf8'
}
headers_pool = [
    {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:12.0) Gecko/20100101 Firefox/12.0'},
    {'User-Agent': 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)'},
    {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.52 Safari/536.5'},
    {'User-Agent': 'Mozilla/5.0 (iPad; U; CPU OS 3_2_1 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Mobile/7B405',
     }
]

ISOTIMEFORMAT="%Y-%m-%d %X"


def get_ss(url):
    """Get ss list from given url

    :param url:
    :return: list of ss addrs like ['ss://xxxxxxx','ss://yyyyy']
    """
    while True:
        try:
            headers = headers_pool[random.randint(0, len(headers_pool)-1)]
            r = requests.get(url, headers=headers, timeout=10)
        except Exception:
            time.sleep(random.randint(2, 10))
            continue
        break

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
    src = os.path.expanduser('~')+'/.cow/rc.bak'
    dst = os.path.expanduser('~')+'/.cow/rc'
    try:
        shutil.copyfile(src, dst)
        f_rc = open(dst, 'a')
        f_rc.write('# other ss proxies\n')
        for ss in ss_list:
            f_rc.write('proxy = {}\n'.format(ss))
        f_rc.close()
        os.system('killall -9 cow')
    except OSError:
        print("Cannot copy file")


def wake_till(seconds):
    """Wake up till reach seconds
    """
    while True:
        if int(time.time()) < seconds:
            time.sleep(5)
        else:
            return


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('should input an url')
        exit()
    else:
        url = sys.argv[1]
        ss_list_old = []
        check_interval = 600  # how many seconds wait for check, auto-adjust
        print("Will fetch info from {}".format(url))
        while True:
            ss_list = get_ss(url)
            if not ss_list:
                print("Get invalid ss list, wait some time to retry")
                time.sleep(random.randint(100,300))
                continue
            if ss_list != ss_list_old: # find new, reduce interval
                print('Get new ss list')
                print('\n'.join(ss_list))
                update_cow(ss_list)
                print('{}: Update'.format(time.strftime(ISOTIMEFORMAT)))
                ss_list_old = ss_list
                check_interval -= random.randint(0, 100)
                print('Adjust next check interval = {}'.format(check_interval))
                current_time = time.time()
                next_seconds = int(current_time) + check_interval
                print('next check time = {}'.format(time.ctime(next_seconds)))
                wake_till(next_seconds)

            else:  # duplicated content, we're checking too quick
                next_wait = random.randint(300, 600)
                check_interval += next_wait
                if check_interval >= 3600*3:  # at most wait for 3 hour
                    check_interval = random.randint(3600*2, 3600*3)
                print('Get duplicated content')
                print('Adjust next check interval = {}'.format(check_interval))
                time.sleep(next_wait)
