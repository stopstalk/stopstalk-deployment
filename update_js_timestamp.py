# -*- coding: utf-8 -*-
"""
    Copyright (c) 2015-2018 Raj Patel(raj454raj@gmail.com), StopStalk

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

all_js_files = ["js/web2py-bootstrap3.min.js",
                "js/appjs/google_analytics.js",
                "js/main.min.js",
                "js/jquery.min.js",
                "js/appjs/layout.min.js",
                "js/appjs/default/contests.min.js",
                "js/appjs/default/faq.min.js",
                "js/appjs/default/filters.min.js",
                "js/appjs/default/search.min.js",
                "js/appjs/default/friends.min.js",
                "js/appjs/default/leaderboard.min.js",
                "js/appjs/default/submissions.min.js",
                "js/appjs/default/todo.min.js",
                "js/materialize-tags.min.js",
                "js/bloodhound.min.js",
                "js/appjs/problems/index.min.js",
                "js/appjs/problems/tag.min.js",
                "js/appjs/problems/trending.min.js",
                "js/appjs/user/profile.js",
                "js/appjs/user/submissions.min.js",
                "js/appjs/problems/editorials.min.js",
                "js/corejs-typeahead.bundle.min.js",
                "js/run_prettify.min.js",
                "js/jquery.bootpag.min.js",
                "js/modernizr-2.8.3.min.js",
                "js/calendar.min.js",
                "js/web2py.min.js",
                "js/appjs/testimonials/index.min.js",
                "js/appjs/google_analytics.js",
                "materialize/css/materialize.min.css",
                "materialize/js/materialize.min.js",
                "css/stopstalk.css",
                "css/style.css",
                "css/calendar.css",
                "css/owlie.css",
                "fa/css/font-awesome.min.css",
                "flag-icon/css/flag-icon.min.css",
                "css/materialize-tags.css",
                "images/favicon.ico",
                "images/favicon.png",
                "images/StopStalk.png",
                "images/svg/users.svg",
                "images/gifs/friends.gif",
                "images/svg/inbox.svg",
                "images/gifs/notifications.jpg",
                "images/svg/user-secret.svg",
                "images/gifs/customfriends.gif",
                "images/svg/calendar-check-o.svg",
                "images/gifs/contestpage.gif",
                "images/svg/eye.svg",
                "images/gifs/viewdownload.gif",
                "images/svg/bar-chart.svg",
                "images/gifs/leaderboardpage.gif",
                "images/svg/line-chart.svg",
                "images/gifs/trending.gif",
                "images/svg/tags.svg",
                "images/gifs/tagpage.gif",
                "images/svg/filter.svg",
                "images/gifs/filterpage.gif",
                "images/svg/user.svg",
                "images/gifs/profilepage.gif",
                "images/codechef_logo.png",
                "images/codeforces_logo.png",
                "images/spoj_logo.png",
                "images/hackerearth_logo.png",
                "images/uva_logo.png",
                "images/hackerrank_logo.png",
                "images/codechef_small.png",
                "images/codeforces_small.png",
                "images/spoj_small.png",
                "images/hackerearth_small.png",
                "images/uva_small.png",
                "images/hackerrank_small.png",
                "images/AC.jpg",
                "images/WA.jpg",
                "images/TLE.jpg",
                "images/MLE.jpg",
                "images/CE.jpg",
                "images/RE.jpg",
                "images/SK.jpg",
                "images/PS.jpg",
                "images/HCK.jpg",
                "images/OTH.jpg",
                "images/bitcoin-accepted-here.png",
                "images/bitcoin-qrcode.png",
                "images/paytm-accepted-here.png",
                "images/paytm-qrcode.png",
                "images/paypal-donate-button.png",
                "images/me.jpg"]

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
            print "Updating timestamp for", filename
            REDIS_CLIENT.set(filename, current_timestamp)
