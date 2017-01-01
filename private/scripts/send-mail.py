"""
    Copyright (c) 2015-2017 Raj Patel(raj454raj@gmail.com), StopStalk

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
query = (atable.registration_key == "") & \
        (atable.blacklisted == False)
rows = db(query).select(atable.stopstalk_handle, atable.email)

for row in rows:
    subject = "UVa Online Judge added on StopStalk"
    message = """
<html>
Hello %s,<br/><br/>

As many of you have requested us to add UVa to StopStalk - here we are with the announcement
that we have successfully added <b>UVa Online Judge</b> to StopStalk.
To update your StopStalk profile with UVa submissions - Add your UVa username / handle <a href="https://www.stopstalk.com/user/update_details">here</a>. <br/>
For your custom users you can update the handles <a href="https://www.stopstalk.com/user/custom_friend">here</a><br/>
Climb the StopStalk leaderboard now ;) <br/><br/>

Also, its been a while since we have conducted a survey to understand your use-cases better and incorporate them to improve StopStalk. <br/>
Please take some minutes to fill out the <a href="https://goo.gl/oeLZHd">Survey Form</a><br/><br/>
Adjust your email preferences <a href="https://www.stopstalk.com/unsubscribe">here</a><br/><br/>
Cheers,<br/>
Team StopStalk
</html>
              """ % (row.stopstalk_handle)
    current.send_mail(to=row.email,
                      subject=subject,
                      message=message,
                      mail_type="feature_updates")
