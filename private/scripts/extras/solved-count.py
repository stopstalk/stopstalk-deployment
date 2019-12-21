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

import pickle

sql_query = """
SELECT problem_link,
       CASE
         WHEN  status = "AC" THEN "AC"
         ELSE "NOT-AC"
       END AS "newstatus",
       COUNT(id) AS "nosubmissions"
FROM submission
GROUP BY  problem_link, newstatus;
            """

print "Executing Count SQL query ..."
result = db.executesql(sql_query)
print "Count SQL Query finished ..."

final_hash = {}

for problem in result:
    if final_hash.has_key(problem[0]):
        if problem[1] == "AC":
            final_hash[problem[0]][0] = problem[2]
        final_hash[problem[0]][1] += problem[2]
    else:
        # List = [#accepted, #total_submissions, #user_ids, #custom_user_ids]
        current_value = [0, 0, "", ""]
        if problem[1] == "AC":
            current_value[0] = problem[2]
        current_value[1] += problem[2]
        final_hash[problem[0]] = current_value

# GROUP_CONCAT default value is 1024 :p (Like who does that!)
# We need = 9 * 1 + 90 * 2 + 900 * 3 + 9000 * 4 + 90000 * 5 +
#           (9 + 90 + 900 + 9000 + 90000)
#         = 488889 + 99999 = 588888
# Always on safer side ;) = 700000
db.executesql("SET GLOBAL group_concat_max_len=700000;")

sql_query = """
SELECT problem_link,
       GROUP_CONCAT(DISTINCT(user_id)) AS user_ids,
       GROUP_CONCAT(DISTINCT(custom_user_id)) AS custom_user_ids
FROM submission
WHERE status="AC"
GROUP BY problem_link;
            """

print "Executing Solved IDs query ..."
result = db.executesql(sql_query)
print "Solved IDs query finished..."

for problem in result:
    final_hash[problem[0]][-2:] = [problem[1], problem[2]]

print "Final hash completely populated ..."

# Serialize the dict for populating it to `problem` table
with open("problem_stats", "wb") as f:
    pickle.dump(final_hash.items(), f)