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

handle = "tryingtocode"
website = "https://www.hackerrank.com/"
response = requests.get("%srest/hackers/%s/rating_histories2" % (website, handle))
response = response.json()["models"]

hackerrank_graphs = []
for contest_class in response:
    final_json = {}
    for contest in contest_class["events"]:
        time_stamp = contest["date"][:-5].split("T")
        time_stamp = datetime.strptime(time_stamp[0] + " " + time_stamp[1],
                                       "%Y-%m-%d %H:%M:%S")
        # Convert UTC to IST
        time_stamp += timedelta(hours=5, minutes=30)
        time_stamp = str(time_stamp)
        final_json[time_stamp] = {"name": contest["contest_name"],
                                  "url": website + contest["contest_slug"],
                                  "rating": contest["rating"],
                                  "rank": contest["rank"]}

    hackerrank_graphs.append({"graph_name": "HackerRank - %s" % contest_class["category"],
                              "graph_data": final_json})

for graph in hackerrank_graphs:
    print graph
