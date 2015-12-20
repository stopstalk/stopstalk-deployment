"""
    Configure StopStalk as required
"""

"""
    Copyright (c) 2015 Raj Patel(raj454raj@gmail.com), StopStalk

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

from gluon import *
from collections import OrderedDict

# List all the profile sites here
# To disable any of the profile site
#   - Just remove that site from the dictionary
# Site Name => user profile url
# OrderedDict is used to maintain the order of insertion
current.SITES = OrderedDict()
current.SITES["CodeChef"] = "http://www.codechef.com/users/"
current.SITES["CodeForces"] = "http://www.codeforces.com/profile/"
current.SITES["Spoj"] = "http://www.spoj.com/users/"
current.SITES["HackerEarth"] = "https://www.hackerearth.com/users/"
current.SITES["HackerRank"] = "https://www.hackerrank.com/"

# If you are under a PROXY uncomment this and comment the next line
#current.PROXY = {"http": "http://proxy.iiit.ac.in:8080/",
#                 "https": "https://proxy.iiit.ac.in:8080/"}

# If you are not under a PROXY
current.PROXY = {}

# The initial date from which the submissions need to be added
current.INITIAL_DATE = "2013-01-01 00:00:00"

# Number of submissions per page
current.PER_PAGE = 100

# Maximum number of requests to make if a website is not responding
current.MAX_TRIES_ALLOWED = 10

# Maximum time that a request can take to return a response(in seconds)
current.TIMEOUT = 15

# Number of problems to be shown in Trending page
current.PROBLEMS_PER_PAGE = 15

# Number of days in the past that should be considered for trending problems
current.PAST_DAYS = 10
