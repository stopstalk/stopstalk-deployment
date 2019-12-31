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

"""
    All this work in vain :p
    There is no need for "category" param
    Itemid is always 8
"""

import requests
from bs4 import BeautifulSoup
judgeurl = "https://uva.onlinejudge.org/"

problem_dict = {}

def is_problem(path):
    if path[0] != "i":
        return "someother"
    params = dict([tuple(x.split("=")) for x in path[10:].split("&")])
    if params.has_key("problem"):
        if problem_dict.has_key(int(params["problem"])):
            problem_dict[int(params["problem"])].append((int(params["Itemid"]),
                                                         int(params["category"])))
        else:
            problem_dict[int(params["problem"])] = [(int(params["Itemid"]),
                                                     int(params["category"]))]
    return params.has_key("problem")

def recurse(tabs, path):
    ret = is_problem(path)
    if ret == "someother":
        return
    print "\t" * tabs, path
    if ret:
        return
    response = requests.get(judgeurl + path)
    soup = BeautifulSoup(response.text, "lxml")

    table = soup.find_all("table")[3]
    current_links = table.find_all("a")
    for link in current_links:
        recurse(tabs + 1, link["href"])

recurse(0, "index.php?option=com_onlinejudge&Itemid=8")
print "******************************"

for key in problem_dict:
    print "[" + str(key) + ", " + str(problem_dict[key]) + "]"
