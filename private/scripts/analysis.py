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

# ==============================================================================
# DEPRECATED
# ==============================================================================

ptable = db.problem
sttable = db.suggested_tags
ttable = db.tag
atable = db.auth_user
stable = db.submission

tags = db(ttable).select()
tags = dict([(x.id, x.value) for x in tags])

new_tags = {}
plinktoid = {}

suggested_tags = db(sttable).select()
for row in suggested_tags:
    if new_tags.has_key(row.problem_id):
        new_tags[row.problem_id].add(tags[row.tag_id])
    else:
        new_tags[row.problem_id] = set([tags[row.tag_id]])

import sys
handle = sys.argv[1]

user = db(atable.stopstalk_handle == handle).select().first()
query = (stable.user_id == user.id) & (stable.status == "AC")
problem_links = db(query).select(stable.problem_link, distinct=True, orderby=stable.time_stamp)
problem_links = [x.problem_link for x in problem_links]

pids = db(ptable.link.belongs(problem_links)).select(ptable.id, ptable.link)
for row in pids:
    plinktoid[row.link] = row.id

for plink in problem_links:
    try:
        print new_tags[plinktoid[plink]]
    except KeyError:
        print []