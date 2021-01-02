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
import re

handle = "tryingtocode"
url = "https://www.codechef.com/users/" + handle

response = requests.get(url)
soup = BeautifulSoup(response.text, "lxml")

script = str(soup.find_all("script")[33])
data = re.findall(r"\[.*?\]", script)

months = {"Jan": ["January", "JAN"],
          "Feb": ["February", "FEB"],
          "Mar": ["March", "MARCH"],
          "Apr": ["April", "APRIL"],
          "May": ["May", "MAY"],
          "Jun": ["June", "JUNE"],
          "Jul": ["July", "JULY"],
          "Aug": ["August", "AUG"],
          "Sep": ["September", "SEPT"],
          "Oct": ["October", "OCT"],
          "Nov": ["November", "NOV"],
          "Dec": ["December", "DEC"]}

long_ratings, long_months, short_ratings, short_months = map(lambda x: eval(x),
                                                             data[:8][1::2])

def zero_pad(string):
    return "0" + string if len(string) == 1 else string

long_contest_data = {}
for i in xrange(len(long_ratings)):
    month, year = long_months[i].split("/")
    year = zero_pad(year)
    time_stamp = str(datetime.strptime(month + " " + year, "%b %y"))
    contest_name = "%s Long Challenge 20%s" % (months[month][0], year)
    contest_url = "https://www.codechef.com/" + months[month][1] + year
    long_contest_data[time_stamp] = {"name": contest_name,
                                     "url": contest_url,
                                     "rating": long_ratings[i]}


short_contest_data = {}
contest_iterator = -1
flag = False

for i in xrange(len(short_ratings)):
    month, year = short_months[i].split("/")
    year = zero_pad(year)
    time_stamp = str(datetime.strptime(month + " " + year, "%b %y"))
    contest_name = "%s Cook off 20%s" % (months[month][0], year)
    contest_iterator += 1
    if contest_iterator == 0:
        # June'10 Cook off has a different URL
        contest_url = "https://www.codechef.com/JUNE10"
    elif contest_iterator == 3 and flag == False:
        # Sept'10 Cook off has a different URL
        contest_url = "https://www.codechef.com/SEPT10"
        contest_iterator -= 1
        flag = True
    else:
        contest_url = "https://www.codechef.com/COOK%s" % zero_pad(str(contest_iterator))
    short_contest_data[time_stamp] = {"name": contest_name,
                                      "url": contest_url,
                                      "rating": short_ratings[i]}

codechef_graphs = [{"graph_name": "CodeChef Long",
                    "graph_data": long_contest_data},
                   {"graph_name": "CodeChef Cook off",
                    "graph_data": short_contest_data}]

for graph in codechef_graphs:
    print graph
