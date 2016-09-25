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

"""
    Run the script on the risk of losing all the submissions
    of all the users and Custom users

    Usage:
    ------
    Go to the web2py directory
    Execute:
        `python web2py.py -S stopstalk -M -R applications/stopstalk/static/scripts/resetDB.py`
    Restart the web2py server
    Open the Index page again
"""
db.submission.truncate()
print "Successfully deleted all submissions"

auth_user_update = db(db.auth_user).update(last_retrieved="2013-01-01 00:00:00")
if auth_user_update:
    print "Update on auth_user completed"
else:
    print "auth_user was not updated"

custom_friend_update = db(db.custom_friend).update(last_retrieved="2013-01-01 00:00:00")
if custom_friend_update:
    print "Update on custom_friend completed"
else:
    print "custom_friend was not updated"

db.commit()
