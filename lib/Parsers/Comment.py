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
import re

from lib.Models.Comment import Comment as CommentDB
from lib.Models.Base import db

logger = logging.getLogger(__name__)

class Comment():

    ''' Parse Requests Content Comments '''

    @staticmethod
    def parse(dburl, content):

        logger.debug('Received %d characters to parse comments for for url: %s' % (len(content), dburl.final_url))
        matches = re.findall('<!--.*?-->', content, re.DOTALL)
        logger.debug('Matched %s comments' % len(matches))

        for match in matches:
            logger.debug('Saving comment %s ' % match)
            with db.execution_context() as ctx:
                CommentDB.create(
                    url = dburl,
                    comment = match
                )

        return
