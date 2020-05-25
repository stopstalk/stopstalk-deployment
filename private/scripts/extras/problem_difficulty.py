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

from gluon import current
from collections import defaultdict
import time

db = current.db

pdtable = db.problem_difficulty
ptable = db.problem
sttable = db.suggested_tags
ttable = db.tag

codeforces_difficulty = {
    "A": 1,
    "B": 2,
    "C": 3,
    "D": 4,
    "E": 5
}

tag_difficulty = {
    "Ad-hoc": 1,
    "Easy": 2,
    "Medium": 3,
    "Hard": 4.5
}

tags = tag_difficulty.keys()

difficulty = defaultdict(list)

# Compute problem difficulty for CodeForces problems.
query = (ptable.link.contains("codeforces")) & \
        ~(ptable.link.contains("gymProblem"))
rows = db(query).select(ptable.id, ptable.link)

for row in rows:
    tag = row.link.split("/")[-1][0]
    pid = row.id

    if tag in codeforces_difficulty:
        difficulty[pid].append(codeforces_difficulty[tag])

# Problems with tags easy, medium, difficult etc.
query = (ttable.value.belongs(tags)) & (ttable.id == sttable.tag_id)
rows = db(query).select(sttable.problem_id, ttable.value)
for row in rows:
    pid = row.suggested_tags.problem_id
    tag = row.tag.value

    difficulty[pid].append(tag_difficulty[tag])

# User suggested problem difficulty.
rows = db(pdtable).select(pdtable.problem_id, distinct=True)
pids = [str(x.problem_id) for x in rows]

sql_query = """
SELECT problem_id, avg(score)
FROM problem_difficulty
WHERE problem_id IN (%(pids)s)
GROUP BY problem_id
HAVING count(*) >= 3
""" % ({"pids": ",".join(pids)})

res = db.executesql(sql_query)
for pid, score in res:
    difficulty[pid].append(float(score))

# Compute average difficulty from all types of problem difficulties.
write_count = 0
for pid, difficulties in difficulty.items():
    if write_count >= 100:
        db.commit()
        write_count = 0
        time.sleep(0.5)

    write_count += 1
    avg_difficulty = sum(difficulties) / float(len(difficulties))
    update = ptable(pid).update_record(difficulty=avg_difficulty)
