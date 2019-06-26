"""
    Copyright (c) 2015-2019 Raj Patel(raj454raj@gmail.com), StopStalk

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
import utilities
import sites

gevent.monkey.patch_all(thread=False)

total_inserted = 0
total_updated = 0
not_updated = 0

# ----------------------------------------------------------------------------
def refresh_tags():
    """
        Refresh tags in the database
    """

    ptable = db.problem

    today = datetime.datetime.now().strftime("%Y-%m-%d")
    before_30 = (datetime.datetime.now() - \
                 datetime.timedelta(30)).strftime("%Y-%m-%d")

    # Problems having tags = ["-"]
    # Possibilities of such case -
    #   => There are actually no tags for the problem
    #   => The problem is from a contest and they'll be
    #      updating tags shortly(assuming 15 days)
    #   => Page was not reachable due to some reason
    query = (ptable.tags_added_on >= before_30) & \
            (ptable.tags == "['-']")
    no_tags = db(query).select(ptable.id)
    no_tags = map(lambda x: x.id, no_tags)

    today = datetime.datetime.now().strftime("%Y-%m-%d")
    threads = []
    workers = 49

    # Start retrieving tags for the problems
    # that are not in problem table
    for i in xrange(0, len(no_tags), workers):
        threads = []
        # O God I am so smart !!
        for problem_id in no_tags[i : i + workers]:
            threads.append(gevent.spawn(get_tag,
                                        problem_id,
                                        today))

        gevent.joinall(threads)

    print "Total Inserted: [%d]" % (total_inserted)
    print "Total Updated: [%d]" % (total_updated)
    print "Total Not-changed: [%d]" % (not_updated)

def get_tag(pid, today):

    global total_inserted
    global total_updated
    global not_updated

    ptable = db.problem
    row = ptable(pid)
    link = row.link
    site = utilities.urltosite(link)

    try:
        Site = getattr(sites, site.lower())
        P = Site.Profile
        if P.is_website_down():
            all_tags = ["-"]
        else:
            tags_func = P.get_tags
            all_tags = tags_func(link)
            if all_tags == []:
                all_tags = ["-"]
    except AttributeError:
        all_tags = ["-"]

    if row:
        prev_tags = row.tags
        if prev_tags != str(all_tags) and prev_tags == "['-']":
            row.update_record(tags=str(all_tags),
                              tags_added_on=today)
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
