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

from lib.Models.History import History as HistoryDB
from lib.Models.HistoryHeader import HistoryHeader as HistoryHeaderDB
from lib.Models.Base import db

logger = logging.getLogger(__name__)

class History():

    ''' Parse Requests History '''

    @staticmethod
    def parse(dburl, history):

        logger.debug('Received %d historical events to parse for url: %s' % (len(history), dburl.final_url))
        for redirect in history:

            logger.debug('Saving %d redirect to %s' % (redirect.status_code, redirect.url))
            with db.execution_context() as ctx:
                db_history = HistoryDB.create(
                    url = dburl,
                    code = redirect.status_code,
                    history_url = redirect.url
                )

            for header in redirect.headers:

                logger.debug('Saving redirection headers %s for url: %s' % (header, redirect.url))
                with db.execution_context() as ctx:
                    HistoryHeaderDB.create(
                        url = dburl,
                        history = db_history,
                        name = header,
                        value = unicode(redirect.headers[header], errors = 'ignore')
                    )

        return
