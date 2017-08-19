# -*- coding: utf-8 -*-
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

import sys, redis
import datetime

all_js_files = ["materialize/js/materialize.js",
                "js/web2py-bootstrap3.js",
                "js/appjs/google_analytics.js",
                "js/main.js",
                "js/appjs/layout.js",
                "js/appjs/default/contests.js",
                "js/appjs/default/faq.js",
                "js/appjs/default/filters.js",
                "js/appjs/default/search.js",
                "js/appjs/default/leaderboard.js",
                "js/appjs/default/submissions.js",
                "js/appjs/default/todo.js",
                "js/materialize-tags.js",
                "js/bloodhound.js",
                "js/appjs/problems/index.js",
                "js/appjs/problems/tag.js",
                "js/appjs/user/profile.js",
                "js/appjs/user/submissions.js"]

REDIS_CLIENT = redis.Redis(host='localhost', port=6379, db=0)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        files = []
    else:
        files = sys.argv[1:]
        if files[0] == "ALL":
            files = all_js_files
    if files != []:
        current_timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        for filename in files:
            REDIS_CLIENT.set(filename, current_timestamp)
