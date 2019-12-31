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

db = current.db
atable = db.auth_user
start = int(sys.argv[1])
end = int(sys.argv[2])

for user_id in xrange(start, end + 1):
    row = db(atable.id == user_id).select(atable.first_name,
                                          atable.last_name,
                                          atable.email,
                                          atable.stopstalk_handle).first()
    if not row:
        continue

    current.send_mail(to=row.email,
                      subject="StopStalk Internationalization",
                      message="""
Hello %s,

Hope you are enjoying StopStalk. Yet again we are planning to come up
with an awesome feature of displaying StopStalk content in your language.
Please take a second (or maybe slightly more) from your busy schedule
to fill up this form - http://goo.gl/forms/snnksBkCcPp8hhPR2

Cheers,
Team StopStalk
                      """ % row.stopstalk_handle,
                      mail_type="feature_updates")
    print "Mail sent to: %s" % (row.first_name + " " + row.last_name)
