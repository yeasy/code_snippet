#!/usr/bin/python
#-*- coding: utf-8 -*-
import re

regex = re.compile('[a-z]{10}')
t1 = re.match(regex,'1234567890')
t2 = re.match(regex,'abcdefghij')

print t1
print t2
