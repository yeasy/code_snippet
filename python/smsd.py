#!/usr/bin/python
#coding: utf8
import urllib2
import re,time,random
from BeautifulSoup import BeautifulSoup

headers_pool=[
    {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'},
    {'User-Agent':'Mozilla/5.0 (compatible;MSIE 9.0; Windows NT 6.1; Trident/5.0)'},
    {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US;) AppleWebKit/534.50(KHTML, like Gecko) Version/5.1 Safari/534.50'}
]
url = "http://www.newsmth.net/bbsdoc.php?board=SecondDigi&ftype=6"

def getPage(headers,url):
    if url == None:
        return
    result = []
    req = urllib2.Request(url,headers=headers)
    response = urllib2.urlopen(req)
    page = response.read()
    pat = re.compile(u"c.o\(.*?\);",re.UNICODE)
    content = page.decode('gb18030','ignore')#.encode('utf8')
    entries = re.findall(pat,content)
    for e in entries:
        f =  e.split(',')
        id,title = f[2],f[5]
        result.append(id+":"+title)
    return result

def getTime():
    return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))


keyword = u"3[cC]|ipad" #The keyword you want to track

if __name__ == "__main__":
    backup=[]
    n = 0
    print "###### start at ", getTime()
    while True:
        n = n+1
        headers = headers_pool[random.randint(0,len(headers_pool)-1)]
        entries = getPage(headers,url)
        if len(entries) <=0:
            continue
        if backup != entries:
            print "######",getTime(),": get new entries =", len(entries)
            for e in entries:
                if re.search(keyword,e):
                    print e
        backup = entries
        time.sleep(random.uniform(2,10))
