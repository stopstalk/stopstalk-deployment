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
from datetime import datetime
import re

handle = "ayanb"
response = requests.get("https://www.hackerearth.com/ratings/AJAX/rating-graph/" + handle)
# if response in REQUEST_FAILURES:
#     print "Request ERROR: HackerEarth " + url + " " + response
#     return
# if response.text == "":
#     print "Request ERROR: HackerEarth " + url + " " + NOT_FOUND
#     return
contest_data = eval(re.findall(r"var dataset = \[.*?\]", response.text)[0][14:])
# if len(contestdata) == 0:
#     return

hackerearth_data = []
for contest in contest_data:
    time_stamp = str(datetime.strptime(contest["event_start"], "%d %b %Y, %I:%M %p"))
    url = "https://www.hackerearth.com" + contest["event_url"]
    hackerearth_data.append({time_stamp: {"name": contest["event_title"],
                                          "rating": contest["rating"],
                                          "url": url,
                                          "rank": contest["rank"]}})
    print time_stamp, name, rating, url
