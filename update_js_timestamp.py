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

import sys, redis
import datetime


def convert_to_min(filename):
    filename = filename.strip()
    if filename[-3:] == ".js":
        filename = filename[:-3] + ".min.js"
    elif filename[-4:] == ".css":
        filename = filename[:-4] + ".min.css"
    return filename


all_image_files = ["images/favicon.ico",
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
                   "images/AC-icon.jpg",
                   "images/WA-icon.jpg",
                   "images/TLE-icon.jpg",
                   "images/MLE-icon.jpg",
                   "images/CE-icon.jpg",
                   "images/RE-icon.jpg",
                   "images/SK-icon.jpg",
                   "images/PS-icon.jpg",
                   "images/HCK-icon.jpg",
                   "images/OTH-icon.jpg",
                   "images/EAC-icon.jpg",
                   "images/bitcoin-accepted-here.png",
                   "images/bitcoin-qrcode.png",
                   "images/paytm-accepted-here.png",
                   "images/paytm-qrcode.png",
                   "images/paypal-donate-button.png",
                   "images/me.jpg",
                   "images/todo_onboarding.gif",
                   "images/write-editorials.gif"]

REDIS_CLIENT = redis.Redis(host='localhost', port=6379, db=0)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        files = []
    else:
        files = sys.argv[1:]
        if files[0] == "ALL":
            with open("static_files_list.txt", "r") as fp:
                all_js_css_files = fp.readlines()

            files = all_js_css_files + all_image_files

        files = map(convert_to_min, files)

    if len(files):
        current_timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        for filename in files:
            print "Updating timestamp for", filename
            REDIS_CLIENT.set(filename, current_timestamp)
