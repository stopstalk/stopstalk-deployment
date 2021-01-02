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

from bs4 import BeautifulSoup
import requests
from datetime import datetime

website = "http://codeforces.com/"
url = "%sapi/contest.list" % website
response = requests.get(url)
contest_list = response.json()["result"]
all_contests = {}

for contest in contest_list:
    all_contests[contest["id"]] = contest

handle = "raj454raj"
url = "%scontests/with/%s" % (website, handle)

response = requests.get(url)
soup = BeautifulSoup(response.text, "lxml")
tbody = soup.find("table", class_="tablesorter").find("tbody")

contest_data = {}
for tr in tbody.find_all("tr"):
    all_tds = tr.find_all("td")
    contest_id = int(all_tds[1].find("a")["href"].split("/")[-1])
    rank = int(all_tds[2].find("a").contents[0].strip())
    solved_count = int(all_tds[3].find("a").contents[0].strip())
    rating_change = int(all_tds[4].find("span").contents[0].strip())
    new_rating = int(all_tds[5].contents[0].strip())
    contest = all_contests[contest_id]
    time_stamp = str(datetime.fromtimestamp(contest["startTimeSeconds"]))
    contest_data[time_stamp] = {"name": contest["name"],
                                "url": "%scontest/%d" % (website, contest_id),
                                "rating": new_rating,
                                "ratingChange": rating_change,
                                "rank": rank,
                                "solvedCount": solved_count}

codeforces_graphs = [{"graph_name": "Codeforces", "graph_data": contest_data}]

for graph in codeforces_graphs:
    print graph
