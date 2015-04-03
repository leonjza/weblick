# The MIT License (MIT)
#
# Copyright (c) 2015 Leon Jacobs
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from app import app
from flask import render_template, url_for, g, abort, redirect
from flask_peewee.utils import object_list, get_object_or_404
from peewee import fn, SQL

from lib.Models.Url import Url
from lib.Models.History import History
from lib.Models.Header import Header
from lib.Models.Cookie import Cookie
from lib.Models.Comment import Comment
from lib.Models.Certificate import Certificate

@app.route('/')
@app.route('/index')
def index():

    counts = {
        'url' : Url.select().count(),
        'header' : Header.select().count(),
        'cookie' : Cookie.select().count(),
        'comment': Comment.select().count(),
        'certificate' : Certificate.select().count()
    }
    return render_template('home.html', counts = counts)

@app.route('/url')
@app.route('/url/<id>')
def url(id = None):

    # with no id specified, we decide on 1
    if id == None:
        return redirect(url_for('url', id = 1))

    # prepare some data for the pagination urls
    id = int(id)
    data = {
        'prev_id': (id - 1) if (id - 1) > 0 else 1,
        'next_id': id + 1
    }

    try:
        data['url'] = Url.get(Url.rank == id)
    except Url.DoesNotExist, e:
        abort(404)

    try:
        data['history'] = History.select().where(History.url == data['url'].id)
    except History.DoesNotExist, e:
        data['history'] = None

    try:
        data['headers'] = Header.select().where(Header.url == data['url'].id)
    except Cookie.DoesNotExist, e:
        data['headers'] = None

    try:
        data['cookies'] = Cookie.select().where(Cookie.url == data['url'].id)
    except Cookie.DoesNotExist, e:
        data['cookies'] = None

    try:
        data['comments'] = Comment.select().where(Comment.url == data['url'].id)
    except Comment.DoesNotExist, e:
        data['comments'] = None

    try:
        data['certificate'] = Certificate.get(Certificate.url == data['url'].id)
    except Certificate.DoesNotExist, e:
        data['certificate'] = None

    return render_template('url.html', data = data)

@app.route('/stats')
def stats():

    data = {}

    # select cookie.name, count(cookie.name) as count from cookie group
    #  by cookie.name order by count desc limit 25;
    data['cookie_names'] = (Cookie
        .select(Cookie.name, fn.COUNT(Cookie.name).alias('num_count'))
        .group_by(Cookie.name)
        .order_by(SQL('num_count').desc())
        .limit(10))

    data['cookie_values'] = (Cookie
        .select(Cookie.value, fn.COUNT(Cookie.value).alias('num_count'))
        .group_by(Cookie.value)
        .order_by(SQL('num_count').desc())
        .limit(10))

    data['header_names'] = (Header
        .select(Header.name, fn.COUNT(Header.name).alias('num_count'))
        .group_by(Header.name)
        .order_by(SQL('num_count').desc())
        .limit(10))

    data['header_values'] = (Header
        .select(Header.value, fn.COUNT(Header.value).alias('num_count'))
        .group_by(Header.value)
        .order_by(SQL('num_count').desc())
        .limit(10))

    return render_template('stats.html', data = data)