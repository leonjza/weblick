#!/usr/bin/python

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

import requests
import logging
import csv
import sys
import os
import time
import signal
import multiprocessing
import ConfigParser
import logging
import traceback

from lib.utils.DBUtils import DB
from lib.utils.Printer import Printer

from lib.Models.Base import db
from lib.Models.Url import Url

from lib.Parsers.Header import Header
from lib.Parsers.Cookie import Cookie
from lib.Parsers.History import History
from lib.Parsers.Comment import Comment
from lib.Parsers.Certificate import Certificate

# read the required configuration
config = ConfigParser.ConfigParser()
config.read('settings.ini')
concurrent_licks = config.getint('lick', 'concurrent_licks')
user_agent = config.get('lick', 'lick_agent')
source_csv = config.get('lick', 'aleksa_csv')

# set up logging to file
# multiprocessing.log_to_stderr(logging.DEBUG)
log_file = os.path.dirname(os.path.realpath(__file__)) + '/' + config.get('lick', 'logfile', 'lick.log')
log_level = logging.INFO
logging.basicConfig(level=log_level, format='%(asctime)s %(processName)-10s %(name)s %(levelname)-8s %(message)s',\
        datefmt='%Y-%m-%d %H:%M:%S', filename=log_file, filemode='a')
logger = logging.getLogger(__name__)

# Make some modules reduce log level verbosity
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("peewee").setLevel(logging.INFO)
logging.getLogger("requests").setLevel(logging.WARNING)

def banner():
    print '''
 __      __      ___.   .____    .__        __
/  \    /  \ ____\_ |__ |    |   |__| ____ |  | __
\   \/\/   // __ \| __ \|    |   |  |/ ___\|  |/ /
 \        /\  ___/| \_\ \    |___|  \  \___|    <
  \__/\  /  \___  >___  /_______ \__|\___  >__|_ \\
       \/       \/    \/        \/       \/     \/
                               v0.1 - @leonjza
                               Use CTRL + \ to exit
    '''
    return

def progress(url):

    with db.execution_context() as ctx:
        p = Url.select().count()
        Printer('Progress: [%.4f%% - %d/1000000] Last processed url: %s' %\
            ((p*100.0 / 1000000), p, (url[:75] + '..') if len(url) > 75 else url))

    return

def process_url(rank_domain):

    # as this will be run in a muliprocessing env, lets
    # attempt to cactch any exceptions and print it
    # so that the pool exception later is more
    # useful
    try:

        ranking = rank_domain[0]
        site_url = 'http://' + rank_domain[1]

        # Do a db lookup to check if we have possibly already processed
        # this url. If we havent, a request will be made to it
        try:

            Url.get(Url.rank == ranking)
            logger.warning('#%s: %s has already been processed. Skipping' % (ranking, site_url))
            return

        except Url.DoesNotExist, e:

            # New url it seems, make a request!
            logger.info('Processing url #%d/1000000 which is: %s' % (ranking, site_url))
            try:

                session = requests.Session()
                headers = { 'User-Agent': user_agent }
                logger.debug('Headers and session setup for request to: %s. Making request' % site_url)
                r = session.get(site_url, headers=headers, timeout=10)

            except Exception, e:

                logger.warning('Failed to retreive %s with error %s' % (site_url, e))
                with db.execution_context() as ctx:
                    Url.create(
                        rank = ranking, domain = rank_domain[1], final_url = None,
                        response_code = 0, is_ok = False, content = None
                    )
                return

        # The request was made and it most probably didnt have
        # any problems. Save it!
        with db.execution_context() as ctx:
            # print r.url, type(r.text)
            data_url = Url.create(
                rank = ranking,
                domain = rank_domain[1],
                final_url = r.url,
                response_code = r.status_code,
                is_ok = True if r.status_code == requests.codes.ok else False,
                # Tired of fighting the unicode errors. Convert to ASCII for now.
                content = r.text.encode('ascii', 'ignore')
            )

        # Move on to the Parsers of the Requests response
        Header.parse(data_url, r.headers)
        Cookie.parse(data_url, session.cookies, session.cookies.get_dict())
        History.parse(data_url, r.history)
        Comment.parse(data_url, r.text)
        # Maybe map.apply_async() this call?
        Certificate.parse(data_url, r.url)

        # Update the progress reporter
        progress(data_url.final_url)

    except Exception, e:
        traceback.print_exc()
        raise e

    return

if __name__ == '__main__':

    banner()

    # prepare a db setup command
    if len(sys.argv) > 1 :
        if sys.argv[1] == 'setupdb':

            logger.debug('Preparing to do database setup')
            DB.setup()
            logger.info('Database succesfully setup')
            print ' * Setup of database `%s` complete' % db.database
            sys.exit(0)

        else:
            print ' * Supported arguments are: setupdb'
            sys.exit(0)

    # Read the Source CSV. Dumping all 1Mil lines' results
    # in like 8MB of memory usage. Woopie
    logger.info('Reading source .csv')
    print ' * Loading source CSV'
    with open(source_csv, 'rb') as csvfile:
        source_data = [(int(line[0]), line[1]) for line in csv.reader(csvfile, delimiter=',')]

    try:

        print ' * Loading the process pool'
        logger.debug('Starting multiprocessing pool with %s concurrent workers' % concurrent_licks)
        pool = multiprocessing.Pool(processes = concurrent_licks)
        pool.map(process_url, source_data, chunksize = 1)

    except KeyboardInterrupt:

        print ' * Caught KeyboardInterrupt, terminating workers'
        logger.warning('Caught KeyboardInterrupt, terminating workers')
        pool.terminate()
