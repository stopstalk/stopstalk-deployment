"""
    Copyright (c) 2015-2020 Raj Patel(raj454raj@gmail.com), StopStalk

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
from datetime import datetime, timedelta
import random
import urllib3
urllib3.disable_warnings()

attable = db.access_tokens
tokens = [(current.neverbounce_user, current.neverbounce_password, "contactstopstalk@gmail.com"),
          (current.neverbounce_user2, current.neverbounce_password2, "raj454raj@gmail.com"),
          (current.neverbounce_user3, current.neverbounce_password3, "admin@stopstalk.com")]

for i in xrange(2):
    # Only 5 tries to get a particular token
    random.shuffle(tokens)
    print tokens[0][2]
    for i in xrange(5):
        response = requests.post('https://api.neverbounce.com/v3/access_token',
                                 auth=HTTPBasicAuth(tokens[0][0],
                                                    tokens[0][1]),
                                 data={"grant_type": "client_credentials",
                                       "scope": "basic user"},
                                 verify=False)
        if response.status_code == 200:
            response = response.json()
            if response.has_key("access_token"):
                attable.insert(value=response["access_token"],
                               type="NeverBounce access_token",
                               time_stamp=datetime.now())
                break

query = (attable.time_stamp < datetime.now() - timedelta(days=2)) & \
        (attable.type == "NeverBounce access_token")
db(query).delete()
