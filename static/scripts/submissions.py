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

import time
import traceback
import gevent
import sys
from datetime import datetime
from gevent import monkey
gevent.monkey.patch_all(thread=False)

# @ToDo: Make this generalised
from sites import codechef, codeforces, spoj, hackerearth, hackerrank
rows = []
atable = db.auth_user
cftable = db.custom_friend

SERVER_FAILURE = "SERVER_FAILURE"
NOT_FOUND = "NOT_FOUND"
OTHER_FAILURE = "OTHER_FAILURE"

INVALID_HANDLES = None

# -----------------------------------------------------------------------------
def _debug(stopstalk_handle, site, custom=False):
    """
        Advanced logging of submissions
    """

    debug_string = stopstalk_handle + " " + site
    if custom:
        debug_string += " CUS"
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
        print "0"
        return 0

    global rows

    for i in sorted(submissions[handle].iterkeys()):
        for j in sorted(submissions[handle][i].iterkeys()):
            submission = submissions[handle][i][j]
            if len(submission) == 7:
                count += 1
                row = []
                if custom:
                    row.extend(["--", user_id])
                else:
                    row.extend([user_id, "--"])

                row.extend([stopstalk_handle,
                            handle,
                            site,
                            submission[0],
                            submission[2],
                            submission[1],
                            submission[5],
                            submission[3],
                            submission[4],
                            submission[6]])

                encoded_row = []
                for x in row:
                    if isinstance(x, basestring):
                        tmp = x.encode("utf-8", "ignore")

                        # @ToDo: Dirty hack! Do something with
                        #        replace and escaping quotes
                        tmp = tmp.replace("\"", "").replace("'", "")
                        if tmp == "--":
                            tmp = "NULL"
                        else:
                            tmp = "\"" + tmp + "\""
                        encoded_row.append(tmp)
                    else:
                        encoded_row.append(str(x))

                rows.append("(" + ", ".join(encoded_row) + ")")


    if count != 0:
        print "%s" % (count)
    else:
        print "0"
    return count

# ----------------------------------------------------------------------------
def handle_not_found(site, site_handle):
    """
        Add this handle to the invalid_handle table

        @param site (String): Profile Site
        @param site_handle (String): Site handle which returned 404
    """

    db.invalid_handle.insert(site=site, handle=site_handle)

# ----------------------------------------------------------------------------
def retrieve_submissions(record, custom):
    """
        Retrieve submissions that are not already in the database
    """

    global INVALID_HANDLES

    time_conversion = "%Y-%m-%d %H:%M:%S"
    list_of_submissions = []

    for site in current.SITES:

        site_handle = record[site.lower() + "_handle"]
        last_retrieved = record[site.lower() + "_lr"]
        last_retrieved = time.strptime(str(last_retrieved), time_conversion)

        if (site_handle, site) in INVALID_HANDLES:
            print "Not found %s %s" % (site_handle, site)
            continue

        if site_handle:
            Site = globals()[site.lower()]
            P = Site.Profile(site_handle)
            site_method = P.get_submissions
            submissions = site_method(last_retrieved)
            if submissions in (SERVER_FAILURE, OTHER_FAILURE):
                print "%s %s %s" % (submissions, site, record.stopstalk_handle)
                return "FAILURE"
            elif submissions == NOT_FOUND:
                print "New invalid handle %s %s" % (site_handle, site)
                handle_not_found(site, site_handle)
                # Update the last retrieved of an invalid handle as we don't
                # want new_user script to pick this user again and again
                record.update({site.lower() + "_lr": datetime.now()})
            else:
                list_of_submissions.append((site, submissions))
                # Immediately update the last_retrieved of the record
                # Note: Only the record object is updated & not reflected in DB
                record.update({site.lower() + "_lr": datetime.now()})

    for submissions in list_of_submissions:
        site = submissions[0]
        _debug(record.stopstalk_handle, site, custom)
        site_handle = record[site.lower() + "_handle"]
        get_submissions(record.id,
                        site_handle,
                        record.stopstalk_handle,
                        submissions[1],
                        site,
                        custom)

    # To reflect all the updates to record into DB
    record.update_record()

    return "SUCCESS"

# ----------------------------------------------------------------------------
def new_users():
    """
        Get the user_ids and custom_user_ids whose any of the last_retrieved
        is equal to INITIAL_DATE

        @return (Tuple): (list of user_ids, list of custom_user_ids)
    """

    def _get_initial_query(table):
        query = False
        for site in current.SITES:
            query |= (table[site.lower() + "_lr"] == current.INITIAL_DATE)
        return query

    max_limit = 3
    query = _get_initial_query(atable) & \
            (atable.blacklisted == False) & \
            (atable.registration_key == "") # Unverified email
    new_users = db(query).select(limitby=(0, max_limit))

    query = _get_initial_query(cftable)
    custom_users = db(query).select(limitby=(0, max_limit))

    return (new_users, custom_users)

# ----------------------------------------------------------------------------
def daily_retrieve():
    """
        Get the user_ids and custom_user_ids for daily retrieval
        according to the param provided (sys.argv[2])

        @return (Tuple): (list of user_ids, list of custom_user_ids)
    """

    N = int(sys.argv[2])
    query = (atable.id % 10 == N) & \
            (atable.blacklisted == False) & \
            (atable.registration_key == "") # Unverified email
    registered_users = db(query).select()

    query = (cftable.id % 10 == N) & (cftable.duplicate_cu == None)
    custom_users = db(query).select()

    return (registered_users, custom_users)

# ----------------------------------------------------------------------------
def re_retrieve():
    """
        Get the user_ids and custom_user_ids whose retrieval was
        failed

        @return (Tuple): (list of user_ids, list of custom_user_ids)
    """

    users = []
    custom_users = []
    frtable = db.failed_retrieval
    rows = db(frtable).select()
    for record in rows:
        if record.user_id:
            users.append(atable(record.user_id))
        else:
            custom_users.append(cftable(record.custom_user_id))

    # Remove all the records after retrieving their submissions
    frtable.truncate()
    return (users, custom_users)

# ----------------------------------------------------------------------------
def specific_user():
    """
        Get the user_ids and custom_user_ids whose retrieval was
        failed

        @return (Tuple): (list of user_ids, list of custom_user_ids)
    """
    custom = (sys.argv[2] == "custom") # Else "normal"
    user_id = int(sys.argv[3])
    users = []
    custom_users = []
    if custom:
        custom_users.append(cftable(user_id))
    else:
        users.append(atable(user_id))
    return (users, custom_users)

if __name__ == "__main__":

    retrieval_type = sys.argv[1]
    if retrieval_type == "new_users":
        users, custom_users = new_users()
    elif retrieval_type == "daily_retrieve":
        users, custom_users = daily_retrieve()
    elif retrieval_type == "re_retrieve":
        users, custom_users = re_retrieve()
    elif retrieval_type == "specific_user":
        users, custom_users = specific_user()
    else:
        print "Invalid arguments"
        sys.exit()

    # Get the handles which returned 404 before
    INVALID_HANDLES = db(db.invalid_handle).select()
    INVALID_HANDLES = set([(x.handle, x.site) for x in INVALID_HANDLES])

    failed_user_ids = []
    for record in users:
        result = retrieve_submissions(record, False)
        if result == "FAILURE":
            failed_user_ids.append(str(record.id))

    failed_custom_user_ids = []
    for record in custom_users:
        result = retrieve_submissions(record, True)
        if result == "FAILURE":
            failed_custom_user_ids.append(str(record.id))

    columns = "(`user_id`, `custom_user_id`, `stopstalk_handle`, " + \
              "`site_handle`, `site`, `time_stamp`, `problem_name`," + \
              "`problem_link`, `lang`, `status`, `points`, `view_link`)"

    if len(rows) != 0:
        sql_query = """INSERT INTO `submission` """ + \
                    columns + """ VALUES """ + \
                    ",".join(rows) + """;"""
        db.executesql(sql_query)

    # Insert user_ids and custom_user_ids into failed_retrieval
    # for which the retrieval failed for further re-retrieval
    insert_query = "INSERT INTO failed_retrieval (user_id, custom_user_id) VALUES"
    if len(failed_user_ids):
        failed_user_ids = ["(" + x + ", NULL)" for x in failed_user_ids]
        sql_query = "%s %s" % (insert_query, ", ".join(failed_user_ids))
        db.executesql(sql_query)

    if len(failed_custom_user_ids):
        failed_custom_user_ids = ["(NULL, " + x + ")" for x in failed_custom_user_ids]
        sql_query = "%s %s" % (insert_query, ", ".join(failed_custom_user_ids))
        db.executesql(sql_query)

# END =========================================================================
