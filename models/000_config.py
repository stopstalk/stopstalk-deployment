"""
    Configure StopStalk as required
"""

from gluon import *
# Site Name => user profile url
current.SITES = {"CodeChef": "http://www.codechef.com/users/",
                 "CodeForces": "http://www.codeforces.com/profile/",
                 "Spoj": "http://www.spoj.com/users/",
                 "HackerEarth": "https://hackerearth.com/users/",
                 "HackerRank": "https://hackerrank.com/"}

current.PROXY = {"http": "http://proxy.iiit.ac.in:8080/",
                 "https": "https://proxy.iiit.ac.in:8080/"}

current.INITIAL_DATE = "2013-01-01 00:00:00"
