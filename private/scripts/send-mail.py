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
    subject = "Get Amazon Gift cards from StopStalk"
    message = """
<html>
Hello %s,<br/><br/>

Since the launch of the platform we have been excited to help you guys be good at Competitive Programming<br/>
and in the process be great at problem solving. Just a slight push at times when you're stuck with a problem<br/>
can result into great learning.<br/><br/>

We support writing editorials on StopStalk for various problems on 7 Competitive Programming websites.<br/>
Contribute to the community and help people with the problems that you have solved.<br/>
Top 3 winners by the end of March will receive Amazon Gift cards from StopStalk - <a style='color: blue;' href="https://www.stopstalk.com/user_editorials?utm_source=newsletter&utm_medium=email&utm_campaign=user-editorials&utm_content=user-editorials-page">Know more.</a><br/><br/>

Cheers,<br/>
Team StopStalk<br/><br/>
<div style='font-size: 10px;color: grey;'>
--------------------------------<br/>
Adjust your email preferences <a style='text-decoration: none; color: grey;' href="https://www.stopstalk.com/unsubscribe?utm_source=newsletter&utm_medium=email&utm_campaign=user-editorials&utm_content=unsubscribe"><u>here</u></a>.<br/><br/>
</div>
</html>
              """ % row.stopstalk_handle
    current.send_mail(to=row.email,
                      subject=subject,
                      message=message,
                      mail_type="feature_updates",
                      bulk=True)