"""
    Copyright (c) 2015-2016 Raj Patel(raj454raj@gmail.com), StopStalk

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

import re
import gevent
from gevent import monkey
import datetime

# @ToDo: Make this generalised
from sites import codechef, codeforces, spoj, hackerearth, hackerrank
gevent.monkey.patch_all(thread=False)

# ----------------------------------------------------------------------------
def urltosite(url):
    """
        Helper function to extract site from url
    """

    # Note: try/except is not added because this function is not to
    #       be called for invalid problem urls
    site = re.search("www\..*\.com", url).group()

    # Remove www. and .com from the url to get the site
    site = site[4:-4]

    return site

# ----------------------------------------------------------------------------
def refresh_tags():
    """
        Refresh tags in the database
    """

    ptable = db.problem_tags
    stable = db.submission

    # Problems that are in problem_tags table
    current_problem_list = db(ptable.id > 0).select(ptable.problem_link)
    # Problems that are in submission table
    updated_problem_list = db(stable.id > 0).select(stable.problem_link,
                                                    distinct=True)
    current_problem_list = map(lambda x: x["problem_link"],
                               current_problem_list)
    updated_problem_list = map(lambda x: x["problem_link"],
                               updated_problem_list)

    today = datetime.datetime.now().strftime("%Y-%m-%d")
    before_10 = (datetime.datetime.now() - datetime.timedelta(10)).strftime("%Y-%m-%d")

    # Problems having tags = ["-"]
    # Possibilities of such case -
    #   => There are actually no tags for the problem
    #   => The problem is from a contest and they'll be
    #      updating tags shortly(assuming 10 days)
    #   => Page was not reachable due to some reason
    query = (ptable.problem_added_on >= before_10)
    query &= (ptable.tags == "['-']")
    no_tags = db(query).select(ptable.problem_link)
    no_tags = map(lambda x: x["problem_link"],
                  no_tags)

    # Compute difference between the lists
    difference_list = list((set(updated_problem_list) - \
                            set(current_problem_list)).union(no_tags))

    print "Refreshing "

    threads = []
    workers = 49

    # Start retrieving tags for the problems
    # that are not in problem_tags table
    for i in xrange(0, len(difference_list), workers):
        threads = []
        # O God I am so smart !!
        for link in difference_list[i : i + workers]:
            threads.append(gevent.spawn(get_tag, link))

        gevent.joinall(threads)

    print "\nNew problems added: " + \
          " [%d]" % (len(difference_list))

def get_tag(link):

    ptable = db.problem_tags
    site = urltosite(link)

    try:
        Site = globals()[site]
        tags_func = Site.Profile().get_tags
        all_tags = tags_func(link)
        if all_tags == []:
            all_tags = ["-"]
    except AttributeError:
        all_tags = ["-"]
    print link, all_tags

    today = datetime.datetime.now().strftime("%Y-%m-%d")
    # Insert tags in problem_tags table
    # Note: Tags are stored in a stringified list
    #       so that they can be used directly by eval
    ptable.update_or_insert(ptable.problem_link == link,
                            problem_link=link,
                            tags=str(all_tags),
                            problem_added_on=today)

if __name__ == "__main__":
    refresh_tags()
