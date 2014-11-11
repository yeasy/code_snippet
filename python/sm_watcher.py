#!/usr/bin/python
#coding: utf8
# Usage: ./prog board_name keyword
# By default, it will show all articles at the couponslife board

import urllib2
import re, time, random, sys

headers_pool=[
    {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'},
    {'User-Agent':'Mozilla/5.0 (compatible;MSIE 9.0; Windows NT 6.1; Trident/5.0)'},
    {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US;) AppleWebKit/534.50(KHTML, like Gecko) Version/5.1 Safari/534.50'}
]

default_board='couponslife'
default_keyword = ".*" #The keyword you want to track
default_url = "http://www.newsmth.net/bbsdoc.php?board=%s&ftype=6" % default_board
default_ct_prefix = "http://www.newsmth.net/bbstcon.php?board=%s&gid=" % default_board


#get a given url page
def getPage(headers,url):
    if not url:
        return
    req = urllib2.Request(url,headers=headers)
    response = urllib2.urlopen(req)
    return response.read()

#get the board content
def getBoard(headers,url):
    '''
    Return articles collection, in format of [[gid,id,ts,title],...]
    :param headers:
    :param url:
    :return:
    '''
    if not url:
        return
    now = time.time()
    result = []
    page = getPage(headers, url)
    pat = re.compile(u"c.o\(.*?\);", re.UNICODE)
    content = page.decode('gb18030', 'ignore')#.encode('utf8')
    entries = re.findall(pat, content)
    for e in entries:
        f =  e.split(',')
        gid, id, ts, title = f[1], f[2], f[4], f[5]
        title = title.strip("' ")
        id = id.strip("' ")
        #print [gid,id,ts,title]
        if id != 'deliver' and now - int(ts) < 3600: # only care recent hour
            result.append([gid, id, ts, title])
    return result

#get the item content
def getItem(headers,url):
    if url == None:
        return
    result = []
    page = getPage(headers,url)
    pat = re.compile(u"c.o\(.*?\);", re.UNICODE)
    content = page.decode('gb18030', 'ignore')#.encode('utf8')
    print content

def getTime(ticks=None):
    t = ticks or time.time()
    return time.strftime('%H:%M:%S',time.localtime(t))
    #return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(t))

if __name__ == "__main__":
    entries_old, interest=[], []
    n = 0
    if len(sys.argv) < 3:
        url, board, keyword, ct_prefix = default_url, default_board, \
                                       default_keyword, default_ct_prefix
    else:
        board,keyword = sys.argv[1], sys.argv[2]
        url = default_url.replace(default_board, board)
        ct_prefix = default_ct_prefix.replace(default_board, board)

    print 'board=%s, keyword=%s' %(board, keyword)
    print "###### start at ", getTime()
    while True:
        n += 1
        flag = False
        headers = headers_pool[random.randint(0, len(headers_pool)-1)]
        try:
            entries = getBoard(headers, url)
        except urllib2.URLError:
            continue
        if len(entries) <= 0:
            continue
        if entries_old != entries:
            for e in entries:
                if re.search(keyword, e[3]):
                    if e not in interest:
                        interest.append(e)
                        flag = True
        if flag:
            print "==============="
            for i in range(len(interest)):
                print '%s %s\n \t\t %s %s' %(getTime(int(interest[i][2])),
                                       interest[i][3], interest[i][1], "URL="+ct_prefix+interest[i][0])
            interest = []
        if len(entries_old) > 100:
            entries_old = entries[100:]
        else:
            entries_old = entries
        time.sleep(random.uniform(1, 5))
