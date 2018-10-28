"""
    Copyright (c) 2015-2018 Raj Patel(raj454raj@gmail.com), StopStalk

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
    subject = "Recent enhancements on StopStalk"
    message = """
<html>
Hello %s,<br/><br/>

We have a few major announcements to make your experience on StopStalk better - <br/>
<ul>
    <li>CodeChef retrieval is now <b>re-enabled</b> and we have successfully integrated CodeChef's new API. Check your updated <a href="https://www.stopstalk.com/user/profile/%s?utm_source=newsletter&utm_medium=email&utm_campaign=important-updates&utm_content=profile-page">StopStalk profile</a> now.</li>
    <li><a href="http://acm.timus.ru/">Timus Online Judge</a> is added to StopStalk. Head over to <a href="https://www.stopstalk.com/user/update_details?utm_source=newsletter&utm_medium=email&utm_campaign=important-updates&utm_content=update-details">Update Details page</a> to add your Timus User ID.</li>
    <li>Spoj retrieval limit of 120 submissions is eliminated and we can now retrieve all your submissions. Please remove your Spoj handle from your profile and then re-add it to fetch all your Spoj submissions.</li>
    <li>You can now write editorials on StopStalk and contribute to the community. Go to any problem page and click on "Editorials" to see editorials contributed by other StopStalkers or write an editorial yourself!</li>
</ul>
Follow our <a href="https://www.facebook.com/stopstalkcommunity">Facebook page</a> for latest updates.<br/>
Adjust your email preferences <a href="https://www.stopstalk.com/unsubscribe?utm_source=newsletter&utm_medium=email&utm_campaign=important-updates&utm_content=unsubscribe">here</a>.<br/><br/>
Cheers,<br/>
Team StopStalk
</html>
              """ % (row.stopstalk_handle, row.stopstalk_handle)
    current.send_mail(to=row.email,
                      subject=subject,
                      message=message,
                      mail_type="feature_updates",
                      bulk=True)
