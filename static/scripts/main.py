"""
    Copyright (c) 2015 Raj Patel(raj454raj@gmail.com), StopStalk

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

import profilesites as p
import time
from datetime import datetime
import gevent
from gevent import monkey
gevent.monkey.patch_all(thread=False)

RED = "\x1b[1;31m"
GREEN = "\x1b[1;32m"
YELLOW = "\x1b[1;33m"
BLUE = "\x1b[1;34m"
MAGENTA = "\x1b[1;35m"
CYAN = "\x1b[1;36m"
RESET_COLOR = "\x1b[0m"

# -----------------------------------------------------------------------------
def _debug(first_name, last_name, site, custom=False):
    """
        Advanced logging of submissions
    """

    name = first_name + " " + last_name
    debug_string = "Retrieving " + \
                   CYAN + site + RESET_COLOR + \
                   " submissions for "
    if custom:
        debug_string += "CUSTOM USER "
    debug_string += BLUE + name + RESET_COLOR
    print debug_string,

# -----------------------------------------------------------------------------
def get_submissions(user_id,
                    handle,
                    stopstalk_handle,
                    submissions,
                    site,
                    custom=False):
    """
        Get the submissions and populate the database
    """

    db = current.db
    count = 0

    if submissions == {}:
        print "[0]"
        return 0

    for i in sorted(submissions[handle].iterkeys()):
        for j in sorted(submissions[handle][i].iterkeys()):
            submission = submissions[handle][i][j]
            if len(submission) == 7:
                count += 1
                args = dict(stopstalk_handle=stopstalk_handle,
                            site_handle=handle,
                            site=site,
                            time_stamp=submission[0],
                            problem_name=submission[2],
                            problem_link=submission[1],
                            lang=submission[5],
                            status=submission[3],
                            points=submission[4],
                            view_link=submission[6])

                if custom is False:
                    args["user_id"] = user_id
                else:
                    args["custom_user_id"] = user_id

                db.submission.insert(**args)

    if count != 0:
        print RED + "[+%s] " % (count) + RESET_COLOR
    else:
        print "[0]"
    return count

# ----------------------------------------------------------------------------
def retrieve_submissions(reg_user, last_retrieved, custom=False):
    """
        Retrieve submissions that are not already in the database
    """

    if custom:
        query = (db.custom_friend.id == reg_user)
        row = db(query).select().first()
    else:
        query = (db.auth_user.id == reg_user)
        row = db(query).select().first()

    list_of_submissions = []

    for site in current.SITES:
        site_handle = row[site.lower() + "_handle"]
        if site_handle:
            P = p.Profile(site, site_handle)
            site_method = getattr(P, site.lower())
            submissions = site_method(last_retrieved)
            list_of_submissions.append((site, submissions))
            if submissions == -1:
                break

    total_retrieved = 0

    for submissions in list_of_submissions:
        if submissions[1] == -1:
            print RED + \
                  "PROBLEM CONNECTING TO " + site + \
                  " FOR " + \
                  row.stopstalk_handle + \
                  RESET_COLOR

            return "FAILURE"

    for submissions in list_of_submissions:
        site = submissions[0]
        site_handle = row[site.lower() + "_handle"]
        _debug(row.first_name, row.last_name, site, custom)
        total_retrieved += get_submissions(reg_user,
                                           site_handle,
                                           row.stopstalk_handle,
                                           submissions[1],
                                           site,
                                           custom)
    return total_retrieved

if __name__ == "__main__":
    time_conversion = "%Y-%m-%d %H:%M:%S"
    lr = open("applications/stopstalk/static/scripts/last_retrieved")
    last_retrieved = lr.read().strip()
    last_retrieved = time.strptime(last_retrieved, time_conversion)
    list_of_submissions = []

    registered_users = db(db.auth_user.id > 0).select(db.auth_user.id)
    for user in registered_users:
        retrieve_submissions(user["id"], last_retrieved)

    custom_users = db(db.custom_friend.id > 0).select(db.custom_friend.id)
    for custom_user in custom_users:
        retrieve_submissions(custom_user["id"], last_retrieved, True)
    lr.close()
    lr = open("applications/stopstalk/static/scripts/last_retrieved", "w")
    today = datetime.now()
    lr.write(str(today)[:-7])
