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

import time
import traceback
import gevent
import sys
import datetime
import utilities
import sites
from gevent import monkey

gevent.monkey.patch_all(thread=False)

rows = []
problem_solved_stats = {}

atable = db.auth_user
cftable = db.custom_friend
nrtable = db.next_retrieval
ptable = db.problem
stable = db.submission

SERVER_FAILURE = "SERVER_FAILURE"
NOT_FOUND = "NOT_FOUND"
OTHER_FAILURE = "OTHER_FAILURE"

TIME_CONVERSION = "%Y-%m-%d %H:%M:%S"
INVALID_HANDLES = None

failed_user_retrievals = []
retrieval_type = None
todays_date = datetime.datetime.today().date()
uva_problem_dict = {}
metric_handlers = {}
plink_to_id = {}
todays_date_string = datetime.datetime.now().strftime("%Y-%m-%d")

# ==============================================================================
class Logger:
    """
        Logger class to print the retrieval status of a user site wise
    """

    # --------------------------------------------------------------------------
    def __init__(self, stopstalk_handle, custom):
        """
            @param stopstalk_handle (String): stopstalk_handle of the user
            @param custom (Boolean): If the user is a custom user or not
        """
        self.stopstalk_handle = stopstalk_handle
        self.custom_str = " CUS" if custom else ""

    # --------------------------------------------------------------------------
    def log(self, site, message):
        """
            Print the log message with the given message for the site

            @param site (String): Site name of the current logline
            @param message (String): Actual message to be logged
        """
        print "%s %s%s %s %s" % (str(datetime.datetime.now()),
                                  self.stopstalk_handle,
                                  self.custom_str,
                                  site,
                                  message)

    # --------------------------------------------------------------------------
    def generic_log(self, message):
        """
            Print the log message with the given message

            @param message (String): Actual message to be logged
        """
        print "%s %s%s %s" % (str(datetime.datetime.now()),
                               self.stopstalk_handle,
                               self.custom_str,
                               message)

# ------------------------------------------------------------------------------
def concurrent_submission_retrieval_handler(action, user_id, custom):
    redis_key = "ongoing_submission_retrieval_"
    redis_key += "custom_user_" if custom else "user_"
    redis_key += str(user_id)

    if action == "GET":
        if current.REDIS_CLIENT.get(redis_key):
            return "ONGOING"
        else:
            return "COMPLETED"
    elif action == "SET":
        current.REDIS_CLIENT.set(redis_key, True, ex=1 * 60 * 60)
    elif action == "DEL":
        current.REDIS_CLIENT.delete(redis_key)

# ------------------------------------------------------------------------------
def populate_uva_problems():
    global uva_problem_dict

    ptable = uvadb.problem
    uvaproblems = uvadb(ptable).select(ptable.problem_id, ptable.title)
    uva_problem_dict = dict([(x.problem_id, x.title) for x in uvaproblems])

# ------------------------------------------------------------------------------
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

    to_be_inserted = set([])
    to_be_updated = set([])
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
            to_be_updated.add(link)
        except KeyError:
            # Problem not in `problem` table
            to_be_inserted.add(link)

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
        today = datetime.datetime.now().strftime("%Y-%m-%d")
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

# ------------------------------------------------------------------------------
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

# ------------------------------------------------------------------------------
def get_submissions(user_id,
                    handle,
                    stopstalk_handle,
                    submissions,
                    site,
                    custom):
    """
        Get the submissions and populate the database
    """

    submission_count = len(submissions)

    if submission_count == 0:
        return submission_count

    for submission in submissions:
        try:
            pname = submission[2].encode("utf-8", "ignore")
        except UnicodeDecodeError:
            pname = str(pname)

        pname = pname.replace("\"", "").replace("'", "")
        plink = submission[1]
        if plink not in plink_to_id:
            pid = ptable.insert(name=pname,
                                link=plink,
                                editorial_link=None,
                                tags="['-']",
                                editorial_added_on=todays_date_string,
                                tags_added_on=todays_date_string,
                                user_ids="",
                                custom_user_ids="")
            plink_to_id[plink] = pid
        else:
            pid = plink_to_id[plink]

        submission_insert_dict = {
            "user_id": user_id if not custom else None,
            "custom_user_id": user_id if custom else None,
            "problem_name": pname,
            "problem_link": plink,
            "stopstalk_handle": stopstalk_handle,
            "site_handle": handle,
            "site": site,
            "time_stamp": submission[0],
            "problem_id": pid,
            "lang": submission[5],
            "status": submission[3],
            "points": submission[4],
            "view_link": submission[6]
        }
        stable.insert(**submission_insert_dict)
        process_solved_counts(plink,
                              pname,
                              submission[3],
                              user_id,
                              custom)

    return submission_count

# ------------------------------------------------------------------------------
def new_handle_not_found(site, site_handle):
    """
        Add this handle to the invalid_handle table

        @param site (String): Profile Site
        @param site_handle (String): Site handle which returned 404
    """

    metric_handlers[site.lower()]["new_invalid_handle"].increment_count("total", 1)
    db.invalid_handle.insert(site=site, handle=site_handle)

# ------------------------------------------------------------------------------
def reorder_leaderboard_data(data):
    """
        @param data (List of List): Each item represent a row in global leaderboard

        @return (List of List): Re-order rows according to rating and assigned ranks
    """
    result = []
    rank = 1

    data = sorted(data, key=lambda x: x[3], reverse=True)
    for row in data:
        result.append((row[0],
                       row[1],
                       row[2],
                       row[3],
                       row[4],
                       row[5],
                       row[6],
                       rank))
        rank += 1

    return result

# ------------------------------------------------------------------------------
def update_stopstalk_rating(user_id, stopstalk_handle, custom):
    atable = db.auth_user
    cftable = db.custom_friend

    column_name = "custom_user_id" if custom else "user_id"
    query = """
    SELECT time_stamp, problem_link, status, site, problem_id
    FROM submission
    WHERE %(column_name)s = %(user_id)d
    ORDER BY time_stamp
            """ % {"column_name": column_name, "user_id": user_id}
    all_submissions = db.executesql(query)

    user_submissions = []
    for submission in all_submissions:
        user_submissions.append({column_name: user_id,
                                 "time_stamp": submission[0],
                                 "problem_link": submission[1],
                                 "status": submission[2],
                                 "site": submission[3],
                                 "problem_id": submission[4]})

    final_rating = utilities.get_stopstalk_user_stats(user_submissions)["rating_history"]
    final_rating = dict(final_rating)
    today = str(datetime.datetime.now().date())
    current_rating = int(sum(final_rating[today]))
    update_params = dict(stopstalk_rating=current_rating)
    if custom:
        cftable(user_id).update_record(**update_params)
    else:
        atable(user_id).update_record(**update_params)

    db.commit()

    # Update global leaderboard cache
    current_value = current.REDIS_CLIENT.get("global_leaderboard_cache")
    if current_value is None:
        # Global leaderboard cache not present
        return current_rating

    import json
    current_value = json.loads(current_value)
    for row in current_value:
        if row[1] == stopstalk_handle:
            row[3] = current_rating
            current_value = reorder_leaderboard_data(current_value)
            current.REDIS_CLIENT.set("global_leaderboard_cache",
                                     json.dumps(current_value),
                                     ex=1 * 60 * 60)
            return current_rating


# ------------------------------------------------------------------------------
def retrieve_submissions(record, custom, all_sites=current.SITES.keys(), codechef_retrieval=False):
    """
        Retrieve submissions that are not already in the database
    """

    global INVALID_HANDLES
    global failed_user_retrievals
    global todays_date
    global metric_handlers

    if concurrent_submission_retrieval_handler("GET", record.id, custom) == "ONGOING":
        print "Already ongoing retrieval for", record.id, custom
        return
    else:
        concurrent_submission_retrieval_handler("SET", record.id, custom)

    stopstalk_retrieval_start_time = time.time()
    sites_retrieval_timings = 0
    list_of_submissions = []
    retrieval_failures = []
    should_clear_cache = False
    nrtable = db.next_retrieval
    user_column_name = "custom_user_id" if custom else "user_id"
    nrtable_record = db(nrtable[user_column_name] == record.id).select().first()
    skipped_retrieval = set([])

    is_daily_retrieval = (retrieval_type == "daily_retrieve")
    logger = Logger(record.stopstalk_handle, custom)

    if nrtable_record is None:
        print "Record not found", user_column_name, record.id
        nrtable.insert(**{user_column_name: record.id})
        nrtable_record = db(nrtable[user_column_name] == record.id).select().first()

    for site in all_sites:
        Site = getattr(sites, site.lower())
        if Site.Profile.is_website_down():
            all_sites.remove(site)

    for site in all_sites:

        lower_site = site.lower()
        site_handle = record[lower_site + "_handle"]
        site_lr = lower_site + "_lr"
        site_delay = lower_site + "_delay"
        last_retrieved = record[site_lr]

        # Rocked it totally ! ;)
        if is_daily_retrieval and \
           datetime.timedelta(days=nrtable_record[site_delay] / 3 + 1) + \
           last_retrieved.date() > todays_date:
            logger.log(site, "skipped")
            metric_handlers[lower_site]["skipped_retrievals"].increment_count("total", 1)
            skipped_retrieval.add(site)
            continue

        last_retrieved = time.strptime(str(last_retrieved), TIME_CONVERSION)

        if (site_handle, site) in INVALID_HANDLES:
            logger.log(site, "not found:" + site_handle)
            metric_handlers[lower_site]["handle_not_found"].increment_count("total", 1)
            record.update({site_lr: datetime.datetime.now()})
            should_clear_cache = True
            continue

        if site_handle:
            Site = getattr(sites, site.lower())
            P = Site.Profile(site_handle)

            # Retrieve submissions from the profile site
            site_method = P.get_submissions
            start_retrieval_time = time.time()
            if site == "UVa":
                submissions = site_method(last_retrieved, uva_problem_dict, is_daily_retrieval)
            else:
                submissions = site_method(last_retrieved, is_daily_retrieval)
            total_retrieval_time = time.time() - start_retrieval_time
            sites_retrieval_timings += total_retrieval_time
            metric_handlers[lower_site]["retrieval_times"].add_to_list("list", total_retrieval_time)
            if submissions in (SERVER_FAILURE, OTHER_FAILURE):
                logger.log(site, submissions)

                metric_handlers[lower_site]["retrieval_count"].increment_count("failure", 1)
                # Add the failure sites for inserting data into failed_retrieval
                retrieval_failures.append(site)
                should_clear_cache = True
                current.REDIS_CLIENT.sadd("website_down_" + site.lower(), record.stopstalk_handle)
            elif submissions == NOT_FOUND:
                logger.log(site, "new invalid handle:" + site_handle)
                new_handle_not_found(site, site_handle)
                # Update the last retrieved of an invalid handle as we don't
                # want new_user script to pick this user again and again
                record.update({site_lr: datetime.datetime.now()})
                should_clear_cache = True
            else:
                submission_len = len(submissions)
                metric_handlers[lower_site]["retrieval_count"].increment_count("success", 1)
                metric_handlers[lower_site]["submission_count"].increment_count("total", submission_len)

                logger.log(site, submission_len)
                list_of_submissions.append((site, submissions))
                # Immediately update the last_retrieved of the record
                # Note: Only the record object is updated & not reflected in DB
                record.update({site_lr: datetime.datetime.now()})
                should_clear_cache = True
        else:
            # Update this time so that this user is not picked
            # up again and again by new_user cron
            record.update({site_lr: datetime.datetime.now()})
            should_clear_cache = True
            if retrieval_type == "daily_retrieve":
                nrtable_record.update({site_delay: 100000})

    total_submissions_retrieved = 0
    for submissions in list_of_submissions:
        site = submissions[0]
        lower_site = site.lower()
        site_delay = lower_site + "_delay"
        submissions_count = get_submissions(record.id,
                                            record[lower_site + "_handle"],
                                            record.stopstalk_handle,
                                            submissions[1],
                                            site,
                                            custom)
        total_submissions_retrieved += submissions_count
        if retrieval_type == "daily_retrieve" and \
           site not in skipped_retrieval and \
           site not in retrieval_failures:
            if submissions_count == 0:
                nrtable_record.update({site_delay: nrtable_record[site_delay] + 1})
            else:
                nrtable_record.update({site_delay: 0})
        elif retrieval_type == "daily_retrieve" and site in retrieval_failures:
            # If retrieval failed for the user, then reset the delay so that
            # the details can be retrieved the next day
            nrtable_record.update({site_delay: 0})

    # Clear the profile page cache in case there is atleast one submission retrieved
    if should_clear_cache:
        utilities.clear_profile_page_cache(record.stopstalk_handle)

    # To reflect all the updates to record into DB
    record.update_record()
    if retrieval_type == "daily_retrieve":
        nrtable_record.update_record()

    if retrieval_type == "refreshed_users" and len(retrieval_failures):
        current.REDIS_CLIENT.rpush("next_retrieve_custom_user" if custom else "next_retrieve_user",
                                   record.id)
    else:
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

    # Keep committing the updates to the db to avoid lock wait timeouts
    db.commit()
    if total_submissions_retrieved > 0:
        log_message = "Rating updated from %f to " % record.stopstalk_rating
        new_rating = update_stopstalk_rating(record.id,
                                             record.stopstalk_handle,
                                             custom)
        log_message += str(new_rating)
        logger.generic_log(log_message)

    concurrent_submission_retrieval_handler("DEL", record.id, custom)
    total_retrieval_time = time.time() - stopstalk_retrieval_start_time
    metric_handlers["overall"]["just_stopstalk_code_time"].add_to_list("list", total_retrieval_time - sites_retrieval_timings)

# ------------------------------------------------------------------------------
def new_users():
    """
        Get the user_ids and custom_user_ids whose any of the last_retrieved
        is equal to INITIAL_DATE

        @return (Tuple): (Dict - (user_id, list of sites),
                          Dict - (custom_user_id, list of sites))
    """

    disabled_sites = current.REDIS_CLIENT.smembers("disabled_retrieval")
    def _get_initial_query(table):
        query = False
        for site in current.SITES:
            if site in disabled_sites:
                continue
            query |= ((table[site.lower() + "_lr"] == current.INITIAL_DATE) & \
                      (table[site.lower() + "_handle"] != ""))
        return query

    max_limit = 10
    query = _get_initial_query(atable) & \
            (atable.blacklisted == False) & \
            (atable.registration_key == "") # Unverified email
    new_users = db(query).select(limitby=(0, max_limit),
                                 orderby="<random>")
    users = {}
    for user in new_users:
        users[user.id] = []
        for site in current.SITES:
            if str(user[site.lower() + "_lr"]) == current.INITIAL_DATE:
                users[user.id].append(site)

    query = _get_initial_query(cftable)
    custom_users = db(query).select(limitby=(0, max_limit),
                                    orderby="<random>")
    cusers = {}
    for user in custom_users:
        cusers[user.id] = []
        for site in current.SITES:
            if str(user[site.lower() + "_lr"]) == current.INITIAL_DATE:
                cusers[user.id].append(site)

    return (users, cusers)

# ------------------------------------------------------------------------------
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

# ------------------------------------------------------------------------------
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
    rows = db(frtable).select(limitby=(0, 20))
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

        record.delete_record()

    return (users, custom_users)

# ------------------------------------------------------------------------------
def specific_users():
    """
        Get the user_ids and custom_user_ids whose retrieval was
        failed

        @return (Tuple): (list of user_ids, list of custom_user_ids)
    """
    custom = (sys.argv[2] == "custom") # Else "normal"
    user_ids = [int(x) for x in sys.argv[3].split(",")]
    users = []
    custom_users = []
    if custom:
        custom_users.extend([cftable(user_id) for user_id in user_ids])
    else:
        users.extend([atable(user_id) for user_id in user_ids])
    return (users, custom_users)

# ------------------------------------------------------------------------------
def refreshed_users():
    """
        Get the user_ids and custom_user_ids who requested for updates

        @return (Tuple): (list of user_ids, list of custom_user_ids)
    """

    custom = (sys.argv[2] == "custom")
    users = set([])
    custom_users = set([])

    if custom:
        while current.REDIS_CLIENT.llen("next_retrieve_custom_user") and \
              len(custom_users) < 10:
            custom_users.add(int(current.REDIS_CLIENT.lpop("next_retrieve_custom_user")))
    else:
        while current.REDIS_CLIENT.llen("next_retrieve_user") and \
              len(users) < 10:
            users.add(int(current.REDIS_CLIENT.lpop("next_retrieve_user")))

    users = [atable(user_id) for user_id in users]
    custom_users = [cftable(user_id) for user_id in custom_users]

    return (users, custom_users)

# ------------------------------------------------------------------------------
def codechef_new_retrievals():
    query = (cftable.codechef_handle != "") & \
            (cftable.codechef_lr == current.INITIAL_DATE)
    custom_friend = db(query).select(orderby="<random>").first()
    if custom_friend is not None:
        return ([], [custom_friend])
    else:
        query = (atable.codechef_lr == current.INITIAL_DATE) & \
                (atable.codechef_handle != "") & \
                (atable.blacklisted == False) & \
                (atable.registration_key == "") # Unverified email

        users = db(query).select(orderby="<random>", limitby=(0, 5))
        return (users, [])

if __name__ == "__main__":

    retrieval_type = sys.argv[1]
    metric_handlers = utilities.init_metric_handlers((retrieval_type == "daily_retrieve"))

    if retrieval_type == "new_users":
        users, custom_users = new_users()
    elif retrieval_type == "daily_retrieve":
        users, custom_users = daily_retrieve()
    elif retrieval_type == "re_retrieve":
        users, custom_users = re_retrieve()
    elif retrieval_type == "specific_users":
        users, custom_users = specific_users()
    elif retrieval_type == "refreshed_users":
        users, custom_users = refreshed_users()
    elif retrieval_type == "codechef_new_retrievals":
        users, custom_users = codechef_new_retrievals()
    else:
        print "Invalid arguments"
        sys.exit()

    populate_uva_problems()

    links = db(ptable).select(ptable.id, ptable.link)
    plink_to_id = dict([(x.link, x.id) for x in links])

    # Get the handles which returned 404 before
    INVALID_HANDLES = db(db.invalid_handle).select()
    INVALID_HANDLES = set([(x.handle, x.site) for x in INVALID_HANDLES])

    if retrieval_type in ("new_users", "re_retrieve"):
        # Note: In this case users and custom_users are dicts
        for user_id in users:
            retrieve_submissions(atable(user_id),
                                 False,
                                 users[user_id],
                                 current.SITES.keys())
        for custom_user_id in custom_users:
            retrieve_submissions(cftable(custom_user_id),
                                 True,
                                 custom_users[custom_user_id],
                                 current.SITES.keys())
    else:
        codechef_retrieval = (retrieval_type == "codechef_new_retrievals")
        for record in users:
            retrieve_submissions(record, False, current.SITES.keys(), codechef_retrieval)
        for record in custom_users:
            retrieve_submissions(record, True, current.SITES.keys(), codechef_retrieval)

    # Just in case the last batch has some residue
    flush_problem_stats()

    # Insert user_ids and custom_user_ids into failed_retrieval
    # for which the retrieval failed for further re-retrieval
    insert_query = "INSERT INTO failed_retrieval (user_id, custom_user_id, site) VALUES "
    if len(failed_user_retrievals):
        sql_query = "%s %s;" % (insert_query, ",".join(failed_user_retrievals))
        db.executesql(sql_query)

# END ==========================================================================
