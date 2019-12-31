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

import utilities
import sys

update_flag = (int(sys.argv[1]) == 1)
db = current.db
atable = db.auth_user
cftable = db.custom_friend

registered_users = db(atable).select()
custom_users = db(cftable).select()

# Find the total solved problems(Lesser than total accepted)
solved_count = {}
sql = """
         SELECT stopstalk_handle, COUNT(DISTINCT(problem_name))
         FROM submission
         WHERE user_id IS NOT NULL AND status = 'AC'
         GROUP BY user_id;
      """
tmplist = db.executesql(sql)
for user in tmplist:
    solved_count[user[0]] = user[1]

complete_dict = {}
for x in registered_users:
    complete_dict[x.stopstalk_handle] = []

for custom_user in custom_users:
    stopstalk_handle = custom_user.stopstalk_handle
    if custom_user.duplicate_cu:
        stopstalk_handle = cftable(custom_user.duplicate_cu).stopstalk_handle
    complete_dict[stopstalk_handle] = []

# Build the complex SQL query
sql_query = """
                SELECT stopstalk_handle, DATE(time_stamp), COUNT(*) as cnt
                FROM submission
                GROUP BY stopstalk_handle, DATE(submission.time_stamp)
                ORDER BY time_stamp;
            """

user_rows = db.executesql(sql_query)

for user in user_rows:
    if user[0] not in complete_dict:
        complete_dict[user[0]] = []
    if complete_dict[user[0]] != []:
        complete_dict[user[0]].append((user[1], user[2]))
    else:
        complete_dict[user[0]] = [(user[1], user[2])]

users = []
for user in registered_users:
    try:
        solved = solved_count[user.stopstalk_handle]
    except KeyError:
        solved = 0

    tup = utilities.compute_row(user,
                                complete_dict,
                                solved,
                                update_flag=update_flag)

sql = sql.replace("user_id", "custom_user_id")
tmplist = db.executesql(sql)

for user in tmplist:
    solved_count[user[0]] = user[1]

for user in custom_users:
    try:
        if user.duplicate_cu:
            orig_user = cftable(user.duplicate_cu)
            solved = solved_count[orig_user.stopstalk_handle]
        else:
            solved = solved_count[user.stopstalk_handle]
    except KeyError:
        solved = 0
    tup = utilities.compute_row(user,
                                complete_dict,
                                solved,
                                custom=True,
                                update_flag=update_flag)
