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

import time
import requests

domain_url = "https://www.codechef.com/"
str_init_time = time.strptime(str(current.INITIAL_DATE),
                              "%Y-%m-%d %H:%M:%S")

def check_valid(handle):

    # Test for invalid handles
    while True:
        response = requests.get(domain_url + "users/" + handle)
        print response.status_code,
        if response.status_code == 200:
            break

    if len(response.history) > 0 and \
       response.history[0].status_code == 302:
        # If user handle is invalid CodeChef
        # redirects to https://www.codechef.com
        return False

    # Actually valid handle with 0 submissions
    return True

ihtable = db.invalid_handle
atable = db.auth_user
cftable = db.custom_friend

rows = db(ihtable.site == "CodeChef").select()
update_params = dict(codechef_lr=current.INITIAL_DATE,
                     rating=0,
                     prev_rating=0,
                     per_day=0.0,
                     per_day_change="0.0")

for row in rows:
    print "{",
    if check_valid(row.handle):
        print row.handle + " VALID",
        query = (atable.codechef_handle == row.handle) & \
                (atable.registration_key == "")

        users = db(query).select()
        for user in users:
            print user.stopstalk_handle + " UPDATED",
            user.update_record(**update_params)
        custom_users = db(cftable.codechef_handle == row.handle).select()
        for custom_user in custom_users:
            print custom_user.stopstalk_handle + " CUS UPDATED",
            custom_user.update_record(**update_params)
        row.delete_record()
    else:
        print row.handle + " INVALID",
    print "}"
