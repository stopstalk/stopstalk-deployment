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

db = current.db
atable = db.auth_user
rows = db(atable.id > 0).select(atable.stopstalk_handle,
                                atable.email)

def get_message(stopstalk_handle):

    message = """

Hello there and Welcome to StopStalk!
We're all set for the release.

Lets get going - """ + URL("default", "user", args=["login"], scheme=True, host=True) + \
"""\n\n Checkout your StopStalk profile page here - """ + URL("user",
                                                              "profile",
                                                              args=[stopstalk_handle],
                                                              scheme=True,
                                                              host=True) + \
"""

If your friends are not on StopStalk - send them your
StopStalk handle and ask them to enter it in
Referrer's StopStalk handle field to get more Custom Users.

You can also add Custom Users if you know their handles
on the Competitive programming sites.

Checkout the Global Leaderboard - """ + URL("default", "leaderboard", scheme=True, host=True) + \
"""

Show your love -
Like us on Facebook - https://www.facebook.com/stopstalkcommunity/
Follow us on Twitter - https://twitter.com/stop_stalk/
Star the Repo on Github - https://github.com/stopstalk/stopstalk/

Lets go StopStalking !!

Cheers,
StopStalk
"""

    return message

for row in rows:
    subject = "Welcome to StopStalk " + row.stopstalk_handle
    current.send_mail(to=row.email,
                      subject=subject,
                      message=get_message(row.stopstalk_handle))
