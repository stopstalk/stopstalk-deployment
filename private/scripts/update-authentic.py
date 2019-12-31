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

db = current.db
atable = db.auth_user

sql = """
         SELECT submission.user_id, submission.site, COUNT( * )
         FROM submission, auth_user
         WHERE submission.user_id = auth_user.id
         GROUP BY auth_user.stopstalk_handle, submission.site
      """

result = db.executesql(sql)
main_dict = {}

for row in result:
    if main_dict.has_key(row[0]):
        if row[2] > 0:
            main_dict[row[0]] += 1
    else:
        if row[2] > 0:
            main_dict[row[0]] = 1

registered_users = db(atable).select(atable.id, atable.authentic)
for user in registered_users:
    if main_dict.has_key(user.id):
        if main_dict[user.id] > 1 and user.authentic is False:
            print user.id, "updated"
            user.update_record(authentic=True)

# END =========================================================================
