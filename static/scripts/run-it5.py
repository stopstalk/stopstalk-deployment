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

import utilities

db = current.db
atable = db.auth_user
cftable = db.custom_friend

afields = ["first_name", "last_name", "stopstalk_handle",
           "institute", "per_day", "rating"]

users = db(atable).select(*afields)
registered_users = []
for user in users:
    registered_users.append(user)

cfields = afields + ["duplicate_cu"]
custom_users = db(cftable).select(*cfields)
custom_friends = []
for custom_user in custom_users:
    custom_friends.append(custom_user)

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

users = []
for user in registered_users:
    try:
        solved = solved_count[user.stopstalk_handle]
    except KeyError:
        solved = 0

    tup = utilities.compute_row(user, solved, update_flag=True)

sql = sql.replace("user_id", "custom_user_id")
tmplist = db.executesql(sql)

for user in tmplist:
    solved_count[user[0]] = user[1]

for user in custom_friends:
    try:
        if user.duplicate_cu:
            orig_user = cftable(user.duplicate_cu)
            solved = solved_count[orig_user.stopstalk_handle]
        else:
            solved = solved_count[user.stopstalk_handle]
    except KeyError:
        solved = 0
    tup = utilities.compute_row(user, solved, custom=True, update_flag=True)
