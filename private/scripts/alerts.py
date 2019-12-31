# -*- coding: utf-8 -*-
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
import datetime

def prettify_dict(d):
    message = ""
    for key in d:
        message += key + ": " + str(d[key]) + "\n"
    return message

sites_dict = {}
for site in current.SITES:
    lower = site.lower()
    site_redis_key = "website_down_" + lower
    sites_dict[lower] = current.REDIS_CLIENT.scard(site_redis_key)
    current.REDIS_CLIENT.delete(site_redis_key)

for site in sites_dict:
    if sites_dict[site] >= 10:
        print requests.post("https://api.pushover.net/1/messages.json",
                      data={"token": current.pushover_api_token,
                            "user": current.pushover_user_token,
                            "message": prettify_dict(sites_dict),
                            "title": "Site down",
                            "priority": 1}).json()
        break

print str(datetime.datetime.now()), prettify_dict(sites_dict).replace("\n", " | ")
