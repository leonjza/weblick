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
from OpenSSL import SSL
from socket import socket
from urlparse import urlparse
import json
import time

from lib.Models.Certificate import Certificate as CertificateDB
from lib.Models.Base import db

logger = logging.getLogger(__name__)

class Certificate():

    ''' Parse a Certificate from a URL '''

    @staticmethod
    def parse(dburl, url):

        logger.debug('Received url %s to attempt certificate parsing' % url)

        # Parse the URL with the aim of getting the final
        # domain out of it.
        o = urlparse(url)

        # ParseResult(scheme='http', netloc='www.google.co.za', path='', params='', query='', fragment='')
        if o.netloc == '':
            return

        # prepare thingies for some SSL talking
        context = SSL.Context(SSL.TLSv1_METHOD) # Use TLS Method
        context.set_options(SSL.OP_NO_SSLv2)    # Don't accept SSLv2
        sock = socket()
        sock.settimeout(10)
        ssl_sock = SSL.Connection(context, sock)

        try:

            # for now, just try the most common tcp/443 port
            ssl_sock.connect((o.netloc, 443))

            # Timeout breaks this cause of the non blocking mode
            # and who knows what else. Lets try implement
            # a patch:
            # https://bitbucket.org/sardarnl/apns-client/pull-request/1/issue-5-retry-on-wantreaderror/diff
            tries = 0
            while True:
                try:

                    ssl_sock.do_handshake()
                    break

                except SSL.WantReadError:

                    tries += 1
                    if tries >= 5:
                        raise

                    time.sleep(0.2)

            # get the certificate. Think this is a PEM
            cert = ssl_sock.get_peer_certificate()

        except Exception, e:

            logger.warning('Failed to connect to %s to get the certificate' % url)
            return

        # Write the information from the certificate to the DB
        try:
            with db.execution_context() as ctx:
                save = CertificateDB.create(
                    url = dburl,
                    issuer_components = unicode(json.dumps(dict(cert.get_issuer().get_components())), errors = 'ignore'),
                    public_key_type = cert.get_pubkey().type(),
                    serial_number = cert.get_serial_number(),
                    signature_algorithm = cert.get_signature_algorithm(),
                    subject_common_name = cert.get_subject().commonName,
                    subject_components = unicode(json.dumps(dict(cert.get_subject().get_components())), errors = 'ignore'),
                    version = cert.get_version(),
                    expired = cert.has_expired(),
                    public_key_bits = cert.get_pubkey().bits()
                )
                logger.debug('Saved certificate information with subject components: %s' % save.subject_components)
        except Exception, e:
            logger.error('Was not able to save the certificate information for %s. Error: %s' % (url, e))

        return
