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

import time
ptable = db.problem
stable = db.submission

links = db(ptable).select(ptable.id, ptable.link)
plink_to_id = dict([(x.link, x.id) for x in links])

BATCH_SIZE = 25000
for i in xrange(10000):
    rows = db(stable).select(limitby=(i * BATCH_SIZE, (i + 1) * BATCH_SIZE))
    print rows.first().id, rows.last().id,
    updated = 0
    for srecord in rows:
        if srecord.problem_id is None and \
           srecord.problem_link in plink_to_id:
            srecord.update_record(problem_id=plink_to_id[srecord.problem_link])
            updated += 1
    if updated > 0:
        db.commit()
        time.sleep(0.1)
        print "updated", updated
    else:
        print "no updates"

