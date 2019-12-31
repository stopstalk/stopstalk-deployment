# -*- coding: utf-8 -*-
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

query = (atable.registration_key == "") & (atable.blacklisted == False)
users = db(query).select(atable.email, atable.stopstalk_handle)

for user in users:
    message = """
<html>
Hey %s,<br/><br/>
We are here to make an important announcement about the way you add friends on StopStalk. <br/>
Friend requests feature is <b>removed</b> completely and now all you need to do is a button click, <br/>
no more waiting for friend requests to get accepted.<br/><br/>

Note: The existing friends are still friends with each other.<br/>
All the pending friend requests are converted into one-way friendship <br/>
(Follower-Followed relationship) - The person who sent the friend request<br/>
has the user added to his/her friend list but not the other way round)
<br/><br/>

Few other enhancements to the site -
<ul>
    <li>You can now suggest tags for a problem</li>
    <li>We have added a <a href="https://www.stopstalk.com/updates">Feature Updates</a> page to keep you updated with the awesome features of StopStalk</li>
    <li>You can now view your submissions on Problem page under "My Submissions" tab</li>
</ul>
Manage your email preferences - <a href="https://www.stopstalk.com/unsubscribe/">here</a>
<br/>
Cheers,<br/>
Team StopStalk
</html>
""" % user.stopstalk_handle
    current.send_mail(to=user.email,
                      subject="Important announcements and updates",
                      message=message,
                      mail_type="feature_updates",
                      bulk=True)
