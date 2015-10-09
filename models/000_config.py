"""
    Configure StopStalk as required
"""

from gluon import *

# List all the profile sites here
# To disable any of the profile site
#   - Just remove that site from the dictionary
# Site Name => user profile url
current.SITES = {"CodeChef": "http://www.codechef.com/users/",
                 "CodeForces": "http://www.codeforces.com/profile/",
                 "Spoj": "http://www.spoj.com/users/",
                 "HackerEarth": "https://hackerearth.com/users/",
                 "HackerRank": "https://hackerrank.com/"}

# If you are under a PROXY uncomment this and comment the next line
#current.PROXY = {"http": "http://proxy.iiit.ac.in:8080/",
#                 "https": "https://proxy.iiit.ac.in:8080/"}

# If you are not under a PROXY
current.PROXY = {}

# The initial date from which the submissions need to be added
current.INITIAL_DATE = "2013-01-01 00:00:00"

# Number of submissions per page
current.PER_PAGE = 100
