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
query = (atable.registration_key != "") & \
        (atable.blacklisted == False)
emails = db(query).select(atable.email)
unverified_emails = set([x.email for x in emails])

rows = db(db.queue.status == "pending").select(orderby="<random>",
                                               limitby=(0, 600))

count = 0
for row in rows:
    if count == 500:
        break
    if row.email in unverified_emails:
        continue
    count += 1
    if bulkmail.send(to=row.email,
                     subject=row.subject,
                     message=row.message):
        row.update_record(status="sent")
        print "Sent to %s %s" % (row.email, row.subject)
    else:
        print "ERROR: " + str(bulkmail.error)
        if str(bulkmail.error).__contains__("Mail rate exceeded limit") is False:
            # Email sending failed with some other reason
            row.update_record(status="failed")
            print "Email sending to %s failed with: %s" % (row.email,
                                                           bulkmail.error)
        else:
            # Email sending failed due to Mail rate
            break
    db.commit()
