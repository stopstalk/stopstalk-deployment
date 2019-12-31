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

import sys
atable = db.auth_user
cftable = db.custom_friend

rating_history_dir = "/home/www-data/web2py/applications/stopstalk/rating_history"
users_dir = rating_history_dir + "/users"
custom_users_dir = rating_history_dir + "/custom_users"
rows = db(atable).select(atable.id, atable.stopstalk_rating)
for row in rows:
    f = open(users_dir + "/" + str(row.id) + ".txt", "a+")
    f.write(str(row.stopstalk_rating) + ",")
    f.close()

rows = db(cftable).select(cftable.id, cftable.stopstalk_rating)
for row in rows:
    f = open(custom_users_dir + "/" + str(row.id) + ".txt", "a+")
    f.write(str(row.stopstalk_rating) + ",")
    f.close()
