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

atable = db.auth_user
iutable = db.institute_user

sql_query = """
SELECT send_to_id, GROUP_CONCAT(user_registered_id)
FROM institute_user
GROUP BY send_to_id;
"""
res = db.executesql(sql_query)
all_user_ids = set([])

for row in res:
    all_user_ids.add(row[0])
    for uid in row[1].split(','):
        all_user_ids.add(int(uid))

id_to_record = {}
rows = db(atable.id.belongs(all_user_ids)).select(atable.id,
                                                  atable.first_name,
                                                  atable.last_name,
                                                  atable.email,
                                                  atable.stopstalk_handle)
for row in rows:
    id_to_record[row.id] = row

def send_message(to_record, from_records):
    names = [str(A(x.first_name + " " + x.last_name,
                   _href=URL("user",
                             "profile",
                             args=x.stopstalk_handle,
                             scheme="https",
                             host="www.stopstalk.com",
                             extension=False))) for x in from_records]

    has_have = ""
    if len(from_records) == 1:
        subject = "Someone registered from your Institute"
        name_string = names[0]
        address_string = "him / her"
        has_have = "has"
    else:
        subject = "A few people registered from your Institute"
        name_string = ", ".join(names[:-1]) + " and " + names[-1]
        address_string = "them"
        has_have = "have"

    message = """
<html>
Hello %s,<br/>
<br/>
%s from your Institute %s just joined StopStalk.<br/>
Add %s as your friend now for better experience on StopStalk.<br/>
<br/>
Adjust your email preferences <a href="%s">here</a><br/>
<br/>
Cheers,<br />
Team StopStalk
</html>
""" % (to_record.stopstalk_handle,
       name_string,
       has_have,
       address_string,
       URL("default",
           "unsubscribe",
           scheme="https",
           host="www.stopstalk.com",
           extension=False))

    current.send_mail(to=to_record.email,
                      subject=subject,
                      message=message,
                      mail_type="institute_user",
                      bulk=True)

for row in res:
    send_message(id_to_record[row[0]],
                 [id_to_record[int(x)] for x in row[1].split(",")])

iutable.truncate()
