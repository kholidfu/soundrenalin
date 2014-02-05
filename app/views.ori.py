#
# views.py
# author: @sopier
# pages: index, search, play, download
#

from flask import render_template, request, redirect
from app import app
import urllib
import json
import re
from xml.etree.ElementTree import parse
from StringIO import StringIO
from filters import slugify
from pymongo import Connection
from pymongo.errors import ConnectionFailure
import subprocess

# make a connection to mongodb server
# this should be goes to __init__.py ??
try:
  c = Connection(host="localhost", port=27017)
except ConnectionFailure, e:
  import sys
  sys.stderr.write("Could not connect to MongoDB: %s" % e)
  sys.exit(1)

# use mydb database
db = c['mydb']

# register slug filter to jinja2 template
@app.template_filter()
def slug(s):
  return slugify(s)

# route for home page / index
@app.route("/")
def index():
  # show data :: limit=1000, sort=descending
  data = db.search.find(limit=1000).sort('_id', -1)

  # show only query with max 5 words on it
  chosen_query = []
  for d in data:
    word_count = len(d['query'].split())
    if word_count < 6:
      chosen_query.append(d)

  querytwenty = chosen_query[:50]

  # return the result
  return render_template('index2.html', data=querytwenty)

@app.route("/about")
def about():
  ref = request.environ.get('HTTP_REFERER')
  # or suggested by someone in forum, this time data already parsed by flask
  # ref = request.headers['REFERER']
  import re
  pattern = re.compile(r"&q=(.*?)&")
  try:
    m = re.search(pattern, ref).group(1)
  except:
    m = 'None'
  return render_template("about.html", ref=m)

@app.route("/music")
def music():
  q = request.args.get('q')
  return redirect("/"+slugify(q)+"/", 301)

@app.route("/<q>/")
def search(q):
  # updating the dbase first
  if q not in ['favicon.ico']:
    db.search.update({"query": q.replace('-', ' ')}, {"$inc": {"count": 1}}, upsert=True)

  url = 'http://gdata.youtube.com/feeds/api/videos?v=2&alt=jsonc&q='+q+'&max-results=30'
  htmldata = urllib.urlopen(url).read()
  jsondata = json.loads(htmldata)

  # handle zero result, show this default video
  if 'items' not in jsondata['data']:
    return render_template('search.html', q=q, datas=[(q,'w9bQAPVo-4g')])

  bigdata = jsondata['data']['items']
  
  # pattern for video id
  pattern = re.compile(r"=(.*?)&feature")

  datas = []

  # our data (tuple)
  for i in range(len(bigdata)):
    title, videoid = (bigdata[i]['title'], re.search(pattern, bigdata[i]['player']['default']).group(1))
    datas.append((title, videoid))

  return render_template('search.html', q=q, datas=datas)

@app.route("/play/<id>/<title>/")
def play(id, title):
  p = subprocess.Popen(["youtube-dl", "--get-url", "http://www.youtube.com/watch?v=" + id], stdout=subprocess.PIPE)
  url = p.stdout.read()
  return render_template('play.html', id=id, title=title, url=url)

@app.route("/mp3/index/<alphabet>/")
def mp3index(alphabet):
  return render_template('mp3index.html', alphabet=alphabet, index=[i for i in db.search.find({"query": {"$regex": "^" + alphabet }}).sort('_id', -1)])



#@app.route("/download/<id>/")
#def download(id):
#  return render_template('download.html', id=id)

#@app.route("/socket.io")
#def run_socketio():
#  return render_template('jug.html')
