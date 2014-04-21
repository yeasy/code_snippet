#!/usr/bin/python
#coding: utf8
import urllib2
import re,time,random,sys
from BeautifulSoup import BeautifulSoup

headers_pool=[
    {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'},
    {'User-Agent':'Mozilla/5.0 (compatible;MSIE 9.0; Windows NT 6.1; Trident/5.0)'},
    {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US;) AppleWebKit/534.50(KHTML, like Gecko) Version/5.1 Safari/534.50'}
]

#get a given url page
def getPage(headers,url):
    if url == None:
        return
    req = urllib2.Request(url,headers=headers)
    response = urllib2.urlopen(req)
    return response.read()

#get the board content
def getBoard(headers,url):
    if url == None:
        return
    result = []
    page = getPage(headers,url)
    pat = re.compile(u"c.o\(.*?\);",re.UNICODE)
    content = page.decode('gb18030','ignore')#.encode('utf8')
    entries = re.findall(pat,content)
    for e in entries:
        f =  e.split(',')
        gid,id,ts,title = f[1],f[2],f[4],f[5]
        #print [gid,id,ts,title]
        result.append([gid,id,ts,title])
    return result

#get the item content
def getItem(headers,url):
    if url == None:
        return
    result = []
    page = getPage(headers,url)
    pat = re.compile(u"c.o\(.*?\);",re.UNICODE)
    content = page.decode('gb18030','ignore')#.encode('utf8')
    print content

def getTime(ticks=None):
    if ticks == None:
        t = time.time()
    else:
        t = ticks
    return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(t))


default_url = "http://www.newsmth.net/bbsdoc.php?board=seconddigi&ftype=6"
default_ct_prefix = "http://www.newsmth.net/bbstcon.php?board=seconddigi&gid="
default_keyword = "3[cC]|ipad" #The keyword you want to track

#Usage: ./prog board_name keyword
if __name__ == "__main__":
    backup,interest=[],[]
    n = 0
    if len(sys.argv) < 3:
        url,keyword,ct_prefix = default_url,default_keyword,default_ct_prefix
    else:
        board,keyword = sys.argv[1],sys.argv[2]
        url = default_url.replace("seconddigi",board)
        ct_prefix = default_ct_prefix.replace("seconddigi",board)

    print "###### start at ", getTime()
    while True:
        n = n+1
        flag = False
        headers = headers_pool[random.randint(0,len(headers_pool)-1)]
        entries = getBoard(headers,url)
        if len(entries) <=0:
            continue
        if backup != entries:
            for e in entries:
                if re.search(keyword,e[3]):
                    if e not in interest:
                        interest.append(e)
                        flag = True
        if flag:
            print "==============="
            for i in range(len(interest)):
                print getTime(int(interest[i][2]))+"--"+interest[i][1]+interest[i][3]+", URL="+ct_prefix+interest[i][0]
        backup = entries
        time.sleep(random.uniform(1,5))
