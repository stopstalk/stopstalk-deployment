"""
    Copyright (c) 2015 Raj Patel(raj454raj@gmail.com), StopStalk

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in
    all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
    THE SOFTWARE.
"""

import re, requests, ast, time
import parsedatetime as pdt
import datetime
import bs4
import gevent
from gevent import monkey
from gluon import current
from bs4 import BeautifulSoup
user_agent = "Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5"
gevent.monkey.patch_all(thread=False)

def get_request(url, headers={}):
    """
        Make a HTTP GET request to a url
    """

    MAX_TRIES_ALLOWED = current.MAX_TRIES_ALLOWED
    i = 0

    while i < MAX_TRIES_ALLOWED:
        try:
            response = requests.get(url,
                                    headers=headers,
                                    proxies=current.PROXY,
                                    timeout=current.TIMEOUT)
        except RuntimeError:
            return -1
        except:
            return {}

        if response.status_code == 200:
            return response
        i += 1

    if response.status_code == 404 or response.status_code == 400:
        return {}

    return -1
