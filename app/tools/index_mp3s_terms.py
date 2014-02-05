#!/usr/bin/env python

import urllib2
import pymongo
import time
import datetime
import re

c = pymongo.Connection()
db = c['indexmp3terms']
#db.term.remove()

while True:
    try:
        opener = urllib2.build_opener()
        opener.addheaders = [('User-agent', 'Googlebot/2.1')]
        data = opener.open('http://www.index-of-mp3s.com').read()
        # data = urllib2.urlopen('http://beemp3.com').read()
    except:
        time.sleep(60)
        continue


    pattern = re.compile(r"black.*?>(.*?) mp3</a>")

    for t in re.findall(pattern, data):
        if t not in ['Null', 'Next', 'Undefined']:
            if 'freemp3x' not in t:
                try:
                    t.decode('ascii')
                    if db.term.find_one({'q': t}):
                        db.term.update({'q': t}, {"$set": {'added': datetime.datetime.now()}, "$inc": {'hits':1}}, upsert=True)
                    else:
                        db.term.insert({'q': t, 'hits': 1, 'added': datetime.datetime.now()})
                except:
                    continue

    time.sleep(10)
