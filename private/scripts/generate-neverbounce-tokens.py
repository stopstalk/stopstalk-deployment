"""
    Copyright (c) 2015-2017 Raj Patel(raj454raj@gmail.com), StopStalk

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

import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime

for i in xrange(2):
    # Only 5 tries to get a particular token
    for i in xrange(5):
        response = requests.post('https://api.neverbounce.com/v3/access_token',
                                 auth=HTTPBasicAuth(current.neverbounce_user,
                                                    current.neverbounce_password),
                                 data={"grant_type": "client_credentials",
                                       "scope": "basic user"})
        if response.status_code == 200:
            response = response.json()
            if response.has_key("access_token"):
                db.access_tokens.insert(value=response["access_token"],
                                        type="NeverBounce access_token",
                                        time_stamp=datetime.now())
                break