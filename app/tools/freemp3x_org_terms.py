#!/usr/bin/env python

import urllib2
import pymongo
import time
import datetime
import re


c = pymongo.Connection()
db = c['terms']
#db.term.remove()

while True:
    try:
        data = urllib2.urlopen('http://freemp3x.org').read()
    except:
        time.sleep(60)
        continue

    pattern = re.compile(r"\.html\">(.*?)</a>&rarr;")

    for t in re.findall(pattern, data):
        print t
    time.sleep(5)
