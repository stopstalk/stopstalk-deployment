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

import time
import traceback
import gevent
import sys
from datetime import datetime
from gevent import monkey
gevent.monkey.patch_all(thread=False)

# @ToDo: Make this generalised
from sites import codechef, codeforces, spoj, hackerearth, hackerrank, uva
rows = []
problem_solved_stats = {}

atable = db.auth_user
cftable = db.custom_friend

SERVER_FAILURE = "SERVER_FAILURE"
NOT_FOUND = "NOT_FOUND"
OTHER_FAILURE = "OTHER_FAILURE"

INVALID_HANDLES = None
failed_user_retrievals = []

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
def insert_this_batch():
    global rows

    columns = "(`user_id`, `custom_user_id`, `stopstalk_handle`, " + \
              "`site_handle`, `site`, `time_stamp`, `problem_name`," + \
              "`problem_link`, `lang`, `status`, `points`, `view_link`)"

    if len(rows) != 0:
        sql_query = """INSERT INTO `submission` """ + \
                    columns + """ VALUES """ + \
                    ",".join(rows) + """;"""
        db.executesql(sql_query)

# -----------------------------------------------------------------------------
def flush_problem_stats():

    global problem_solved_stats

    def _stringify(given_set):
        return [str(x) for x in given_set]

    if len(problem_solved_stats) == 0:
        # No processing required
        return

    # Get the existing user_ids and custom_user_ids for taking union
    ptable = db.problem
    query = (ptable.link.belongs(problem_solved_stats.keys()))
    existing = db(query).select(ptable.link,
                                ptable.user_ids,
                                ptable.custom_user_ids)

    existing_ids = {}
    for row in existing:
        val = [set([]), set([])]
        if row.user_ids:
            val[0] = set([int(x) for x in row.user_ids.split(",")])
        if row.custom_user_ids:
            val[1] = set([int(x) for x in row.custom_user_ids.split(",")])
        existing_ids[row.link] = val

    solved_case = ""
    total_case = ""
    user_ids_case = ""
    custom_user_ids_case = ""

    def _build_when(link, value, column_name=None):
        res = ""
        if column_name:
            res = "WHEN '%s' THEN %s + %d\n" % (link, column_name, value)
        else:
            value = ",".join(_stringify(value))
            res = "WHEN '%s' THEN '%s'\n" % (link, value)
        return res

    to_be_inserted = []
    to_be_updated = []
    for link in problem_solved_stats:
        val = problem_solved_stats[link]
        try:
            # val[2] = user_ids who solved the problem in this retrieval
            # existing_ids[link][0] = user_ids who have already solved the problem
            if val[2].issubset(existing_ids[link][0]) is False:
                user_ids_case += _build_when(link,
                                             val[2].union(existing_ids[link][0]))

            # val[3] = custom_user_ids who solved the problem in this retrieval
            # existing_ids[link][1] = custom_user_ids who have already solved the problem
            if val[3].issubset(existing_ids[link][1]) is False:
                custom_user_ids_case += _build_when(link,
                                                    val[3].union(existing_ids[link][1]))

            # Add to the CASE statement only if there is an update
            if val[0]:
                solved_case += _build_when(link, val[0], "solved_submissions")
            total_case += _build_when(link, val[1], "total_submissions")
            to_be_updated.append(link)
        except KeyError:
            # Problem not in `problem` table
            to_be_inserted.append(link)

    if len(to_be_updated):
        non_empty_components = []
        def _build_component(column_name, value):
            if value:
                non_empty_components.append("""
%s = CASE link
%s
     ELSE %s END""" % (column_name, value, column_name))

        _build_component("solved_submissions", solved_case)
        _build_component("total_submissions", total_case),
        _build_component("user_ids", user_ids_case),
        _build_component("custom_user_ids", custom_user_ids_case)

        sql_query = """
UPDATE problem
SET
%s
WHERE link in (%s);
                    """ % (",".join(non_empty_components),
                           ",".join(["'" + x + "'" for x in to_be_updated]))

        db.executesql(sql_query)

    if len(to_be_inserted):
        sql_query = ""
        today = datetime.now().strftime("%Y-%m-%d")
        insert_value = ""
        value_string = "(" + ",".join(["\"%s\""] * 8) + ",%s,%s)"
        for plink in to_be_inserted:
            val = problem_solved_stats[plink]
            insert_value += value_string % (plink,
                                            val[4],
                                            "['-']",
                                            "",
                                            ",".join(_stringify(val[2])),
                                            ",".join(_stringify(val[3])),
                                            today,
                                            today,
                                            val[0],
                                            val[1])
            insert_value += ","

        insert_value = insert_value[:-1]
        insert_query = """
INSERT INTO problem (link, name, tags, editorial_link, user_ids, custom_user_ids, tags_added_on, editorial_added_on, solved_submissions, total_submissions)
VALUES %s
                       """ % (insert_value)

        db.executesql(insert_query)

    # Flush the actual dict
    problem_solved_stats = {}

# -----------------------------------------------------------------------------
def process_solved_counts(problem_link, problem_name, status, user_id, custom):
    if problem_solved_stats.has_key(problem_link) is False:
        # [solved_submissions, total_submissions, user_ids, custom_user_ids]
        problem_solved_stats[problem_link] = [0, 0, set([]), set([]), problem_name]

    value_list = problem_solved_stats[problem_link]
    value_list[1] += 1
    if status == "AC":
        value_list[0] += 1
        value_list[3].add(user_id) if custom else value_list[2].add(user_id)

    if len(problem_solved_stats) > 100:
        flush_problem_stats()

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
                        try:
                            tmp = x.encode("utf-8", "ignore")
                        except UnicodeDecodeError:
                            tmp = str(tmp)

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

                process_solved_counts(encoded_row[7].strip("\""),
                                      encoded_row[6].strip("\""),
                                      encoded_row[9].strip("\""),
                                      user_id,
                                      custom)

                rows.append("(" + ", ".join(encoded_row) + ")")
                if len(rows) > 1000:
                    insert_this_batch()
                    rows = []

    if count != 0:
        print str(count)
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
def retrieve_submissions(record, custom, all_sites=current.SITES):
    """
        Retrieve submissions that are not already in the database
    """

    global INVALID_HANDLES
    global failed_user_retrievals

    if "CodeChef" in all_sites:
        all_sites.remove("CodeChef")

    time_conversion = "%Y-%m-%d %H:%M:%S"
    list_of_submissions = []
    retrieval_failures = []
    plink_to_id = {}

    if "CodeForces" in all_sites:
        ptable = db.problem
        query = ptable.link.contains("codeforces")
        problem_records = db(query).select(ptable.id,
                                           ptable.link,
                                           ptable.tags)
        for problem_record in problem_records:
            plink_to_id[problem_record.link] = (problem_record.tags,
                                                problem_record.id)

    for site in all_sites:

        site_handle = record[site.lower() + "_handle"]
        site_lr = site.lower() + "_lr"
        last_retrieved = record[site_lr]
        last_retrieved = time.strptime(str(last_retrieved), time_conversion)

        if (site_handle, site) in INVALID_HANDLES:
            print "Not found %s %s" % (site_handle, site)
            record.update({site_lr: datetime.now()})
            continue

        if site_handle:
            Site = globals()[site.lower()]
            P = Site.Profile(site_handle)
            site_method = P.get_submissions
            if site == "CodeForces":
                submissions = site_method(last_retrieved, plink_to_id)
            else:
                submissions = site_method(last_retrieved)
            if submissions in (SERVER_FAILURE, OTHER_FAILURE):
                print "%s %s %s" % (submissions, site, record.stopstalk_handle)
                # Add the failure sites for inserting data into failed_retrieval
                retrieval_failures.append(site)
            elif submissions == NOT_FOUND:
                print "New invalid handle %s %s" % (site_handle, site)
                handle_not_found(site, site_handle)
                # Update the last retrieved of an invalid handle as we don't
                # want new_user script to pick this user again and again
                record.update({site_lr: datetime.now()})
            else:
                list_of_submissions.append((site, submissions))
                # Immediately update the last_retrieved of the record
                # Note: Only the record object is updated & not reflected in DB
                record.update({site_lr: datetime.now()})
        else:
            # Update this time so that this user is not picked
            # up again and again by new_user cron
            record.update({site_lr: datetime.now()})

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

    # @ToDo: Too much main memory usage as strings are stored in a list
    #        Aim to store only the ints and let typecasting and
    #        "NULL" insertions happen just when required
    for site in retrieval_failures:
        if custom:
            failed_user_retrievals.append("(%s,%s,'%s')" % ("NULL",
                                                            str(record.id),
                                                            site))
        else:
            failed_user_retrievals.append("(%s,%s,'%s')" % (str(record.id),
                                                            "NULL",
                                                            site))

# ----------------------------------------------------------------------------
def new_users():
    """
        Get the user_ids and custom_user_ids whose any of the last_retrieved
        is equal to INITIAL_DATE

        @return (Tuple): (Dict - (user_id, list of sites),
                          Dict - (custom_user_id, list of sites))
    """

    def _get_initial_query(table):
        query = False
        for site in current.SITES:
            query |= (table[site.lower() + "_lr"] == current.INITIAL_DATE)
        return query

    max_limit = 5
    query = _get_initial_query(atable) & \
            (atable.blacklisted == False) & \
            (atable.registration_key == "") # Unverified email
    new_users = db(query).select(limitby=(0, max_limit))
    users = {}
    for user in new_users:
        users[user.id] = []
        for site in current.SITES:
            if str(user[site.lower() + "_lr"]) == current.INITIAL_DATE:
                users[user.id].append(site)

    query = _get_initial_query(cftable)
    custom_users = db(query).select(limitby=(0, max_limit))
    cusers = {}
    for user in custom_users:
        cusers[user.id] = []
        for site in current.SITES:
            if str(user[site.lower() + "_lr"]) == current.INITIAL_DATE:
                cusers[user.id].append(site)

    return (users, cusers)

# ----------------------------------------------------------------------------
def daily_retrieve():
    """
        Get the user_ids and custom_user_ids for daily retrieval
        according to the param provided (sys.argv[2])

        @return (Tuple): (list of user_ids, list of custom_user_ids)
    """

    M = int(sys.argv[2])
    N = int(sys.argv[3])
    query = (atable.id % M == N) & \
            (atable.blacklisted == False) & \
            (atable.registration_key == "") # Unverified email
    registered_users = db(query).select()

    query = (cftable.id % M == N) & (cftable.duplicate_cu == None)
    custom_users = db(query).select()

    return (registered_users, custom_users)

# ----------------------------------------------------------------------------
def re_retrieve():
    """
        Get the user_ids and custom_user_ids whose retrieval was
        failed

        @return (Tuple): (Dict - (user_id, list of sites failures),
                          Dict - (custom_user_id, list of site failures))
    """

    users = {}
    custom_users = {}
    frtable = db.failed_retrieval
    rows = db(frtable).select()
    for record in rows:
        if record.user_id:
            if users.has_key(record.user_id):
                users[record.user_id].add(record.site)
            else:
                users[record.user_id] = set([record.site])
        elif record.custom_user_id:
            if custom_users.has_key(record.custom_user_id):
                custom_users[record.custom_user_id].add(record.site)
            else:
                custom_users[record.custom_user_id] = set([record.site])

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

    if retrieval_type in ("new_users", "re_retrieve"):
        # Note: In this case users and custom_users are dicts
        for user_id in users:
            retrieve_submissions(atable(user_id),
                                 False,
                                 users[user_id])
        for custom_user_id in custom_users:
            retrieve_submissions(cftable(custom_user_id),
                                 True,
                                 custom_users[custom_user_id])
    else:
        for record in users:
            retrieve_submissions(record, False)
        for record in custom_users:
            retrieve_submissions(record, True)

    # Just in case the last batch has some residue
    insert_this_batch()
    flush_problem_stats()

    # Insert user_ids and custom_user_ids into failed_retrieval
    # for which the retrieval failed for further re-retrieval
    insert_query = "INSERT INTO failed_retrieval (user_id, custom_user_id, site) VALUES "
    if len(failed_user_retrievals):
        sql_query = "%s %s;" % (insert_query, ",".join(failed_user_retrievals))
        db.executesql(sql_query)

# END =========================================================================
