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
from datetime import datetime, timedelta

attable = db.access_tokens

response = requests.post("https://api.codechef.com/oauth/token",
                         data={"grant_type": "client_credentials",
                               "scope": "public",
                               "client_id": current.codechef_client_id,
                               "client_secret": current.codechef_client_secret,
                               "redirect_uri": ""})
json_data = response.json()

if response.status_code == 200 and json_data["status"] == "OK":
    attable.insert(value=json_data["result"]["data"]["access_token"],
                   type="CodeChef access_token",
                   time_stamp=datetime.now())
else:
    print "Error requesting CodeChef API for access token"

query = (attable.time_stamp < datetime.now() - timedelta(days=2)) & \
        (attable.type == "CodeChef access_token")
db(query).delete()
