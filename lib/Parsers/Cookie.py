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

import logging
import requests

from lib.Models.Cookie import Cookie as CookieDB
from lib.Models.Base import db

logger = logging.getLogger(__name__)

class Cookie():

    ''' Parse Requests Cookies '''

    @staticmethod
    def parse(dburl, cookie_values, all_cookies):

        for cookie in all_cookies:

            try:

                logger.debug('Saving cookie %s as %s' % (cookie, cookie_values[cookie]))
                with db.execution_context() as ctx:
                    CookieDB.create(
                        url = dburl,
                        name = cookie,
                        value = unicode(cookie_values[cookie], errors = 'ignore')
                    )

            except KeyError, e:
                logger.warning('Failed to read cookie %s with error %s' % (cookie, e))

            except requests.cookies.CookieConflictError, e:
                logger.warning('Duplicate cookie %s exists' % cookie)

        return
