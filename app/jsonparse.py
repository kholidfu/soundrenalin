#!/usr/bin python

import json

# use loads method

#with open('data.json') as f:
#    data = f.read()
#    jsondata = json.loads(data)

#for row in jsondata['rows']:
#    print row['title']


# or use load (without s) method

with open('data.json') as f:
    jsondata = json.load(f)

for row in jsondata['rows']:
    print row['score']

# use loads if you want to parse from string buffer, otherwise, use load method
# bye ....
