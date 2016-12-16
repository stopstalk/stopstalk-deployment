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
import utilities

# @ToDo: Make this generalised
from sites import codechef, codeforces, spoj, hackerearth, hackerrank
gevent.monkey.patch_all(thread=False)

total_inserted = 0
total_updated = 0
not_updated = 0

# ----------------------------------------------------------------------------
def refresh_editorials():
    """
        Refresh editorial links in the database
    """

    ptable = db.problem
    stable = db.submission

    # Problems that are in problem table
    current_problem_list = db(ptable).select(ptable.link)

    # Problems that are in submission table
    updated_problem_list = db(stable).select(stable.problem_link,
                                             distinct=True)
    current_problem_list = [x.link for x in current_problem_list]
    updated_problem_list = [x.problem_link for x in updated_problem_list]

    today = datetime.datetime.now().strftime("%Y-%m-%d")
    before_15 = (datetime.datetime.now() - \
                 datetime.timedelta(15)).strftime("%Y-%m-%d")

    query = ((ptable.editorial_added_on == None) |
             (ptable.editorial_added_on >= before_15)) & \
            (ptable.editorial_link == None)
    no_editorial = db(query).select(ptable.link)
    no_editorial = [x.link for x in no_editorial]

    # Compute difference between the lists
    difference_list = list((set(updated_problem_list) - \
                            set(current_problem_list)).union(no_editorial))

    today = datetime.datetime.now().strftime("%Y-%m-%d")

    threads = []
    workers = 49

    # Start retrieving tags for the problems
    # that are not in problem table
    for i in xrange(0, len(difference_list), workers):
        threads = []
        # O God I am so smart !!
        for plink in difference_list[i : i + workers]:
            threads.append(gevent.spawn(get_editorial, plink, today))

        gevent.joinall(threads)

    print "Total Inserted: [%d]" % (total_inserted)
    print "Total Updated: [%d]" % (total_updated)
    print "Total Not-changed: [%d]" % (not_updated)

def get_editorial(link, today):

    global total_inserted
    global total_updated
    global not_updated

    ptable = db.problem
    site = utilities.urltosite(link)

    Site = globals()[site]
    editorial_func = Site.Profile().get_editorial_link
    editorial_link = editorial_func(link)

    row = db(ptable.link == link).select().first()
    if row:
        if editorial_link:
            row.update_record(editorial_link=editorial_link,
                              editorial_added_on=today)
            print "Updated", link, "->", editorial_link
            total_updated += 1
        else:
            not_updated += 1
            print "No-change", link
    else:
        print "****************Should not be here****************"
        total_inserted += 1
        print "Inserted", link, editorial_link
        # Intentional raising error to fix the issue
        1 / 0
        # Insert editorial_link in problem table
        ptable.insert(link=link,
                      editorial_link=editorial_link,
                      editorial_added_on=today,
                      tags_added_on=today)

if __name__ == "__main__":

    total_inserted = 0
    total_updated = 0
    not_updated = 0
    refresh_editorials()
