"""
    Configure StopStalk as required
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
