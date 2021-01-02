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

db = current.db
atable = db.auth_user
cftable = db.custom_friend

today = datetime.datetime.today().date()
start = datetime.datetime.strptime(current.INITIAL_DATE,
                                   "%Y-%m-%d %H:%M:%S").date()
total_days = (today - start).days

sql_query = """
                SELECT user_id, custom_user_id, COUNT(*) as cnt
                FROM submission
                GROUP BY user_id, custom_user_id
            """

res = db.executesql(sql_query)
user_submissions = {}
custom_user_submissions = {}

for user in res:
    if user[0]:
        user_submissions[user[0]] = user[2]
    else:
        custom_user_submissions[user[1]] = user[2]

users = db(atable).select()
custom_users = db(cftable).select()

for user in users:
    if user_submissions.has_key(user.id):
        curr_per_day = user_submissions[user.id] * 1.0 / total_days
        change = "%0.5f" % (curr_per_day - user.per_day)
        user.update_record(per_day_change=change)

for custom_user in custom_users:
    cid = custom_user.id
    if custom_user.duplicate_cu:
        cid = custom_user.duplicate_cu
    if custom_user_submissions.has_key(cid):
        curr_per_day = custom_user_submissions[cid] * 1.0 / total_days
        change = "%0.5f" % (curr_per_day - custom_user.per_day)
        custom_user.update_record(per_day_change=change)

