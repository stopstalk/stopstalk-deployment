"""
    Copyright (c) 2015-2020 Raj Patel(raj454raj@gmail.com), StopStalk

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

stable = db.submission
atable = db.auth_user
cftable = db.custom_friend
ptable = db.problem
sttable = db.suggested_tags
ttable = db.tag

submissions = db(stable.user_id == 31).select(orderby=stable.time_stamp)
plinks = set([x.problem_link for x in submissions])
rows = db(ptable.link.belongs(plinks)).select()
link_to_id = dict([(x.link, [x.id, x.solved_submissions, x.total_submissions]) for x in rows])
res = db.executesql("""
    SELECT problem_id, GROUP_CONCAT(tag_id) as tags
    FROM suggested_tags
    GROUP BY problem_id
""")

pid_to_tags = dict([(x[0], set(x[1].split(","))) for x in res])
tags = db(ttable).select(ttable.id, ttable.value)
tags = dict([(x.id, x.value) for x in tags])
plink_to_tags = {}
till_now = set([])

def get_problem_tags(link):
    try:
        tag_ids = pid_to_tags[link_to_id[link][0]]
    except KeyError:
        return
    return [tags[int(x)] for x in tag_ids], link_to_id[link][1] * 100.0 / link_to_id[link][2]

prev_link = None
for submission in submissions:
    if submission.problem_link == prev_link:
        continue
    if submission.problem_link not in plink_to_tags:
        plink_to_tags[submission.problem_link] = get_problem_tags(submission.problem_link)
    if plink_to_tags[submission.problem_link] is not None:
        print plink_to_tags[submission.problem_link][1]
    prev_link = submission.problem_link
