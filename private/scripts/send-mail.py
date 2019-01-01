"""
    Copyright (c) 2015-2019 Raj Patel(raj454raj@gmail.com), StopStalk

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
    subject = "StopStalk Job Profile"
    message = """
<html>
Hello %s,<br/><br/>

We are here with an amazing announcement for you guys.<br/>
You might be looking for Job or Internship opportunites while you are busy solving interesting problems.<br/>
Let us know if you are interested in being contacted by companies looking to hire candidates like you.<br/><br/>

Update your <a href="https://www.stopstalk.com/job_profile?utm_source=newsletter&utm_medium=email&utm_campaign=job-profile&utm_content=job-page">StopStalk Job Profile</a> now by filling the required details on the page and we will contact you if we find a match.<br/>
We hope we can find you an apt place for your skills to grow.<br/><br/>

Cheers,<br/>
Team StopStalk<br/><br/>

--------------------------------<br/>
Adjust your email preferences <a href="https://www.stopstalk.com/unsubscribe?utm_source=newsletter&utm_medium=email&utm_campaign=job-profile&utm_content=unsubscribe">here</a>.<br/><br/>
</html>
              """ % row.stopstalk_handle
    current.send_mail(to=row.email,
                      subject=subject,
                      message=message,
                      mail_type="feature_updates",
                      bulk=True)
