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

total_inserted = 0
total_updated = 0
not_updated = 0

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

    ptable = db.problem
    stable = db.submission

    # Problems that are in problem table
    current_problem_list = db(ptable).select(ptable.link,
                                             ptable.name)

    # Problems that are in submission table
    updated_problem_list = db(stable).select(stable.problem_link,
                                             stable.problem_name,
                                             distinct=True)
    current_problem_list = map(lambda x: (x.link, x.name),
                               current_problem_list)
    updated_problem_list = map(lambda x: (x.problem_link, x.problem_name),
                               updated_problem_list)

    today = datetime.datetime.now().strftime("%Y-%m-%d")
    before_15 = (datetime.datetime.now() - \
                 datetime.timedelta(15)).strftime("%Y-%m-%d")

    # Problems having tags = ["-"]
    # Possibilities of such case -
    #   => There are actually no tags for the problem
    #   => The problem is from a contest and they'll be
    #      updating tags shortly(assuming 15 days)
    #   => Page was not reachable due to some reason
    query = (ptable.tags_added_on >= before_15)
    query &= (ptable.tags == "['-']")
    no_tags = db(query).select(ptable.link,
                               ptable.name)
    no_tags = map(lambda x: (x.link, x.name), no_tags)

    # Compute difference between the lists
    difference_list = list((set(updated_problem_list) - \
                            set(current_problem_list)).union(no_tags))

    today = datetime.datetime.now().strftime("%Y-%m-%d")
    threads = []
    workers = 49

    # Start retrieving tags for the problems
    # that are not in problem table
    for i in xrange(0, len(difference_list), workers):
        threads = []
        # O God I am so smart !!
        for problem in difference_list[i : i + workers]:
            threads.append(gevent.spawn(get_tag,
                                        problem[0],
                                        problem[1],
                                        today))

        gevent.joinall(threads)

    print "Total Inserted: [%d]" % (total_inserted)
    print "Total Updated: [%d]" % (total_updated)
    print "Total Not-changed: [%d]" % (not_updated)

def get_tag(link, name, today):

    global total_inserted
    global total_updated
    global not_updated

    ptable = db.problem
    site = urltosite(link)

    try:
        Site = globals()[site]
        tags_func = Site.Profile().get_tags
        all_tags = tags_func(link)
        if all_tags == []:
            all_tags = ["-"]
    except AttributeError:
        all_tags = ["-"]

    # If record already exists only update
    # name and tags not problem_added_on
    row = db(ptable.link == link).select().first()

    if row:
        prev_tags = row.tags
        if prev_tags != str(all_tags):
            row.update_record(tags=str(all_tags),
                              name=name,
                              tags_added_on=today,
                              editorial_added_on=today)
            print "Updated", link, prev_tags, "->", all_tags
            total_updated += 1
        else:
            not_updated += 1
            print "No-change", link
    else:
        total_inserted += 1
        print "Inserted ", link, all_tags
        # Insert tags in problem table
        # Note: Tags are stored in a stringified list
        #       so that they can be used directly by eval
        row = [link, name, str(all_tags), today]
        ptable.insert(link=link,
                      tags=str(all_tags),
                      name=name,
                      tags_added_on=today,
                      editorial_added_on=today)

if __name__ == "__main__":

    total_inserted = 0
    total_updated = 0
    not_updated = 0
    refresh_tags()
