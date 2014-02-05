#!/usr/bin/python
#: @author: @sopier
#: date: 23-May-2013
#: place: bumiayu

import urllib2
import json
from urllib import urlencode
from pprint import pprint

base_url = 'http://api.indeed.com/ads/'

class Indeed(object):
    base_url = 'http://api.indeed.com/ads/'

    def jobsearch(q):
        pass

    def jobdetail(jobkey):
        pass

query = 'java'
location = 'austin'
country_code = 'us'

action = 'apisearch'
query_params = {
    'q': query,
    'l': location,
    'co': country_code,
    'format': 'json',
    'v': '2',
    'publisher': '9183314218030936',
}

query_params = dict([ (k, v) for (k, v) in query_params.items()])
query_string = urlencode(query_params)
request_url = '{0}{1}?{2}'.format(base_url, action,query_string)

request = urllib2.urlopen(request_url)
results = request.read()

# we've got the data
data = json.loads(results)

# get jobkey and store them into array container
jobkeys = []
for key in data['results']:
    jobkeys.append(key['jobkey'])

#print jobkeys

# for each jobkey, get detailed jobs
jobdetailaction = 'apigetjobs'
query_params2 = {
    'jobkeys': jobkeys[0],
    'format': 'json',
    'v': '2',
    'publisher': '9183314218030936'
}

query_string2 = urlencode(query_params2)
request_url2 = '{0}{1}?{2}'.format(base_url, jobdetailaction, query_string2)

#print request_url2

request2 = urllib2.urlopen(request_url2)
results2 = request2.read()
data2 = json.loads(results2)

pprint(data2)

# insert into mongodb
