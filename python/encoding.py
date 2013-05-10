#!/usr/bin/python
#-*-coding:utf-8-*-
#if there is no default encoding declaration, then local system encoding will be used as default.

import sys
print sys.getdefaultencoding()

#test the unicode object
s = u"中文" #an unicode object, just use encode
try:
    print "s=",s #use default encoding (utf-8 here) to interpret
    print "s.utf-8=",s.encode('utf-8')
    print "s.gbk=",s.encode('gbk')
except:
    pass
finally:
    pass

#test the string: character sequence
s = "中文" #string will be encoded with default file encoding (utf-8 here), decode into unicode first.
try:
    print "s=",s
    print "s.utf-8=",s.decode('utf-8').encode('utf-8')
    print "s.gbk=",s.decode('utf-8').encode('gbk')
except:
    pass
finally:
    pass
