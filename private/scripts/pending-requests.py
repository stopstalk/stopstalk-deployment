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

####################################################################
#         DEPRECATED AFTER ADDING `following` table
####################################################################

db = current.db
atable = db.auth_user
frtable = db.friend_requests

join_query = (atable.id == frtable.to_h)
email_ids = db(frtable).select(atable.email,
                               join=frtable.on(join_query),
                               distinct=True)

for email in email_ids:

    current.send_mail(to=email["email"],
                      subject="You have pending requests!",
                      message=
"""<html>
Hello StopStalker!! <br />

You have pending friend requests on StopStalk <br />
Connect with more to make best use of StopStalk - %s <br />

To stop receiving mails - <a href="%s">Unsubscribe</a> <br />
Cheers, <br />
StopStalk
</html>
""" % (URL("default", "notifications",
           scheme="https",
           host="www.stopstalk.com"),
       URL("default", "unsubscribe",
           scheme="https",
           host="www.stopstalk.com")),
                      mail_type="pending_requests",
                      bulk=True)

# END =========================================================================
