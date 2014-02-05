#
# views.py
# author: @sopier
# pages: index, search, play, download
#

from flask import render_template, request, redirect, send_from_directory
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
import random
import redis
import datetime
import urllib2 

# redis connect
r = redis.Redis()

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
  # db terms colongan
  # termsdb = c['terms']
  # db from search box
  searchdb = c['mydb']

  # popular terms sorted based on hits (most popular)
  # data = termsdb.term.find().sort('hits', -1).limit(50)

  # latest terms inserted
  # data = searchdb.search.find().sort('_id', -1).limit(50)

  # pake terms1
  # data = searchdb.terms1.find().sort('_id', -1).limit(50)

  # pake terms2
  # murni keyword dari search box aja
  data = searchdb.terms2.find().sort('_id', -1).limit(50)

  # latest terms

  # random terms colongan
  #termscount = termsdb.term.find().count()
  #data = [i for i in termsdb.term.find().skip(random.randint(0, int(termscount))).limit(50)]

  # return the result
  return render_template('index2.html', data=data)

@app.route("/about")
def about():
  # ref = request.environ.get('HTTP_REFERER')
  # or suggested by someone in forum, this time data already parsed by flask
  #ref = request.headers['REFERER']
  #import re
  #pattern = re.compile(r"&q=(.*?)&")
  #try:
  #  m = re.search(pattern, ref).group(1)
  #except:
  #  m = 'None'
  return render_template("about.html")

@app.route("/robots.txt")
def robots():
  return send_from_directory(app.static_folder, request.path[1:])

@app.route("/music")
def music():
  q = request.args.get('q')
  db.terms2.insert({'query': q.replace('-', ' ')})
  return redirect("/"+slugify(q)+"/", 301)

# latest terms collections started on July 07, 2013
db.terms1.ensure_index('query')

@app.route("/<q>/")
def search(q):
  # dmca request
  if q in ['el-wawa', 'echous', 'podhum-podhum-kadhal-podhum-yaaradi-nee-mohini', 'nogomi-mix', 'alaya-me', 'ya-8ali', 'nancy-ajram-ya-kethar-live-2011', 'lamsit', 'najwa-karam-asmarani', 'hena-hena', 'taratil', 'aziza-jalal', 'majida-el-roumi-lbc-advertisement', 'creepy-ass-pony-;o-amnesia:-custom-story-part-3-the-small-horse-part-b', 'aghani-7ob', 'soliman-f', 'etamen-tamer-hosny', 'enta-omri-hossam-ramzy', 'tamer-hosny-habibi-ya-rasoul-allah', 'clear-choice', 'saree-k-fall-sa-r-rajkumar-hindi-movie', 'r-rajkumar-hindi-movie-songs', 'rajkumar', 'r-rajkumar-s-photos']:
    return redirect('/', 301)

  # Block baidu bot
  if 'Baidu' in request.user_agent.string:
    return redirect('/', 301)

  # updating the dbase first
  #if q not in ['favicon.ico']:
  #  db.search.update({"query": q.replace('-', ' ')}, {"$inc": {"count": 1}}, upsert=True)

  #if q not in['favicon.ico']:
    #db.terms1.insert({'query': q.replace('-', ' ')})

  url = 'http://gdata.youtube.com/feeds/api/videos?v=2&alt=jsonc&q='+q+'&max-results=30'
  htmldata = urllib.urlopen(url).read()
  jsondata = json.loads(htmldata)


  # handle zero result, show this default video
  if 'items' not in jsondata['data']:
    # menambahkan tanggal
    tanggal = datetime.datetime.now()
    # menambahkan angka random sebagai fake file size
    fsize = random.randint(30, 70)

    return render_template('search.html', q=q, datas=[(q,'w9bQAPVo-4g')], tanggal=tanggal, fsize=fsize)

  bigdata = jsondata['data']['items']
  
  # pattern for video id
  pattern = re.compile(r"=(.*?)&feature")

  datas = []

  # our data (tuple)
  for i in range(len(bigdata)):
    title, videoid = (bigdata[i]['title'], re.search(pattern, bigdata[i]['player']['default']).group(1))
    datas.append((title, videoid))

  # random terms data

  # if redis exist, use it, else query db
  if r.lrange('terms', 0, -1):
    terms = r.lrange('terms', 0, -1)
  else:
    # termsdb = c['terms'] # jupukan lawas
    termsdb = c['indexmp3terms'] # anyar 5-nov-2013
    termscount = termsdb.term.find().count()
    terms_data = [i['q'] for i in termsdb.term.find().skip(random.randint(0, int(termscount))).limit(20)]

    for t in terms_data:
      r.rpush('terms', t)

    terms = r.lrange('terms', 0, 20)
    r.expire('terms', 60)

  # njagani kalo terms masih kosong, biar gak error
  if not terms:
    terms = [i['q'] for i in termsdb.term.find().skip(random.randint(0, int(termscount))).limit(20)]

  # Googlebot detection
  if 'Googlebot' not in request.headers['User-Agent']:
    terms = []  

  # menambahkan tanggal
  tanggal = datetime.datetime.now()

  # menambahkan angka random sebagai fake file size
  fsize = random.randint(30, 70)

  return render_template('search.html', q=q, datas=datas, terms=terms, tanggal=tanggal, fsize=fsize)

@app.route("/play/<id>/<title>/")
def play(id, title):
  return render_template('play.html', id=id, title=title)

@app.route("/download/<id>/<title>/")
def download(id, title):
  #p = subprocess.Popen(["youtube-dl", "--get-url", "http://www.youtube.com/watch?v=" + id], stdout=subprocess.PIPE)
  #url = p.stdout.read()

  # Block baidu bot
  if 'Baidu' in request.user_agent.string:
    return redirect('/', 301)

  url = '#'
  return render_template('download.html', id=id, title=title, url=url)

@app.route("/popular")
def popular():
  url = "http://www.youtube.com/playlist?list=PL55713C70BA91BD6E"
  pattern = re.compile(r"ltr\">(.*?)</span>")
  html = urllib2.urlopen(url).read()

  titles = re.findall(re.compile(r"ltr\">(.*?)</span>"), html)
  return render_template("popular.html", titles=titles)

@app.route("/mp3/index/<alphabet>/")
def mp3index(alphabet):
  #return render_template('mp3index.html', alphabet=alphabet, index=[i for i in db.search.find({"query": {"$regex": "^" + alphabet }}).sort('_id', -1)])
  return redirect('/', 301)

#@app.route("/download/<id>/")
#def download(id):
#  return render_template('download.html', id=id)

#@app.route("/socket.io")
#def run_socketio():
#  return render_template('jug.html')

@app.route("/debug")
def debag():
  from flask import url_for
  data = {}
  data.update({'root': request.url_root})
  data.update({'url_for': url_for('index')})
  data.update({'app_name': app.config['SERVER_NAME']})
  return render_template("debag.html", data=data)
