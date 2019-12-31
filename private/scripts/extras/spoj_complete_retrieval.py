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

import requests, bs4, re

handle = "pranjalr34"
response = requests.get("https://www.spoj.com/users/%s/" % handle)
soup = bs4.BeautifulSoup(response.text, "lxml")
tds = soup.find_all("td")
all_problem_names = []
for td in tds:
    try:
        atag = td.contents[0]
        if re.match("/status/.*,%s/" % handle, atag["href"]) and atag.text != "":
            all_problem_names.append(atag.text)
    except:
        pass

print all_problem_names


#for problem_name in all_problem_names:
#    print "https://www.spoj.com/status/%s,%s/" % (problem_name, handle)
