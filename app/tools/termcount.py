#!/usr/bin/env python
import pymongo

c = pymongo.Connection()
db = c['terms']
print db.term.find().count()
