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

import datetime
import json
import re
import time
from socket import gethostname

from boto3 import client
from gluon import (BUTTON, DIV, H5, HR, IMG, INPUT, OPTION, SELECT, SPAN,
                   TABLE, TAG, TBODY, TD, TEXTAREA, TH, THEAD, TR, URL, A, I,
                   current)
from gluon.storage import Storage
from requests.exceptions import ConnectionError

from health_metrics import MetricHandler
from influxdb_wrapper import get_series_helper
from stopstalk_constants import *


# -----------------------------------------------------------------------------
def is_apicall():
    """
        Check whether the request has an API Token
        If it has an api_token then requset its an API Call
    """
    api_token = current.request.vars.get("api_token", None)
    return api_token in current.api_tokens

# -----------------------------------------------------------------------------
def check_api_token(function):
    """
        API Token Checking Decorator
    """
    def verifier(*args, **kwargs):
        if is_apicall():
            token = current.request.vars['api_token']
            allowed_tokens = current.api_tokens
            # check if the API call has a valid authentication token
            if token not in allowed_tokens:
                current.response.status = 401
                return current.response.json('Token is invalid')
            current.request.extension = 'json'
        return function(*args, **kwargs)
    return verifier

# -----------------------------------------------------------------------------
def check_api_userauth(function):
    """
        API Token with userauth Checking Decorator
    """
    @current.auth_jwt.allows_jwt()
    @check_api_token
    @current.auth.requires_login()
    def verifier(*args, **kwargs):
        if current.session.user_id is None:
            current.session.user_id = current.auth.user_id
        return function(*args, **kwargs)
    return verifier

# -----------------------------------------------------------------------------
def check_api_user(function):
    """
        API Token with user Checking Decorator
        Login is not required
    """
    if not is_apicall():
        def verifier(*args, **kwargs):
            return function(*args, **kwargs)
        return verifier

    current.request.ajax = False
    @check_api_token
    @current.auth_jwt.allows_jwt(function)
    def verifier(*args, **kwargs):
        if current.session.user_id is None and current.auth.is_logged_in():
            current.session.user_id = current.auth.user_id
        return function(*args, **kwargs)
    return verifier

# -----------------------------------------------------------------------------
def get_gauth_key(auth_token):
    return "g_token_" + auth_token

# -----------------------------------------------------------------------------
def get_codechef_last_retrieved_key(record_id, custom):
    return "codechef:last_retrieved:%d:%s" % (record_id, str(custom))

# -----------------------------------------------------------------------------
def get_reminder_button(contest):
    return A(I(_class="fa fa-calendar-plus-o"),
             _class="btn-floating btn-small accent-4 tooltipped orange set-reminder",
             _href=URL("calendar", "u",
                       scheme="https",
                       host="calendar.google.com",
                       args=["0", "r", "eventedit"],
                       vars={"text": "Contest at " + contest["site"] + ": " + contest["name"],
                             "dates": "%s/%s" % (contest["start_time"].strftime("%Y%m%dT%H%M00"),
                                                 contest["end_time"].strftime("%Y%m%dT%H%M00")),
                             "ctz": "Asia/Kolkata",
                             "details": "<b>Event created from <a href='https://www.stopstalk.com'>StopStalk</a></b>\n" + \
                                        "_____________________________\n\n"
                                        "<b>Link:</b> <a href='%s'>Contest Link</a>\n" % contest["url"] + \
                                        "<b>Site:</b> %s\n" % contest["site"] + \
                                        "<b>Duration:</b> %s" % get_duration_string(int(float(contest["duration"]))),
                             "location": contest["url"],
                             "sf": "true",
                             "output": "xml"},
                       extension=False),
             _target="_blank",
             data=dict(tooltip=current.T("Set Reminder to Google Calendar"),
                       position="left",
                       delay="50"))

# -----------------------------------------------------------------------------
def gauth_redirect(token):
    import requests
    resp = requests.post("https://oauth2.googleapis.com/tokeninfo", data={"id_token": token})
    data = resp.json()
    user_email = data["email"]
    user = current.db.auth_user(**{"email": user_email})
    if not user:
        user_info = {
            "g_token": data["sub"],
            "first_name": data["given_name"],
            "last_name": data["family_name"] if "family_name" in data else "",
            "email": user_email
        }
        user_info = json.dumps(user_info)
        current.REDIS_CLIENT.set(get_gauth_key(data["sub"]), user_info, ex=1 * 60 * 20)
        return URL("user", "fill_details", vars={"g_token": data["sub"]})
    current.auth.login_user(user)
    return URL("default", "dashboard")

#--------------------------------------------------------------------------------
def get_jwt_gauth_app(token):
    import requests
    resp = requests.post("https://oauth2.googleapis.com/tokeninfo", data={"id_token": token})
    if resp.status_code != 200:
        return None
    data = resp.json()
    user_email = data["email"]
    user = current.db.auth_user(**{"email": user_email})
    if not user:
        return None
    current.auth.login_user(user)
    return current.auth_jwt.jwt_token_manager()

# -----------------------------------------------------------------------------
def get_jwt_token_from_request():
    """
    The method that extracts and validates the token from the header
    """
    token = None
    token_in_header = current.request.env.http_authorization
    if token_in_header:
        parts = token_in_header.split()
        if parts[0].lower() == 'bearer' and len(parts) == 2:
            token = parts[1]
    return token

# -----------------------------------------------------------------------------
def push_influx_data(measurement, points, app_name="cron"):

    # if current.environment != "production":
    # Temporarily commenting out the data insert for disk issues
    return

    try:
        SeriesHelperClass = get_series_helper(
                                measurement,
                                INFLUX_MEASUREMENT_SCHEMAS[measurement]["fields"],
                                INFLUX_MEASUREMENT_SCHEMAS[measurement]["tags"]
                            )

        if isinstance(points, dict):
            points = [points]

        for point in points:
            point.update(host=gethostname(),
                         app_name=app_name)
            SeriesHelperClass(**point)

        SeriesHelperClass.commit()
    except ConnectionError:
        print "Can't connect to influxdb"
        return

# -----------------------------------------------------------------------------
def get_problem_mappings(db_obj, table, fields):
    problems = db_obj(table).select(table[fields[0]], table[fields[1]])
    return dict([(x[fields[0]], x[fields[1]]) for x in problems])

# -----------------------------------------------------------------------------
def is_stopstalk_admin(user_id):
    return user_id in STOPSTALK_ADMIN_USER_IDS

# -----------------------------------------------------------------------------
def get_key_from_dict(actual_dict, key, no_key_value):
    try:
        return actual_dict[key]
    except KeyError:
        return no_key_value

# -----------------------------------------------------------------------------
def is_valid_stopstalk_handle(handle):
    try:
        group = re.match("[0-9a-zA-Z_]*", handle).group()
        return (group == handle) and handle[:4] != "cus_"
    except AttributeError:
        return False

# -----------------------------------------------------------------------------
def add_language_to_cache(language):
    if language in ["", "-"]:
        return

    current.REDIS_CLIENT.sadd("all_submission_languages", language)
    return

# -----------------------------------------------------------------------------
def prepend_custom_identifier(form):
    form.vars.stopstalk_handle = "cus_" + form.vars.stopstalk_handle

# -----------------------------------------------------------------------------
def init_metric_handlers(log_to_redis):

    metric_handlers = {}
    genre_to_kind = {"submission_count": "just_count",
                     "retrieval_count": "success_failure",
                     "skipped_retrievals": "just_count",
                     "handle_not_found": "just_count",
                     "new_invalid_handle": "just_count",
                     "retrieval_times": "average",
                     "request_stats": "success_failure",
                     "request_times": "average"}

    # This should only log if the retrieval type is the daily retrieval
    for site in current.SITES:
        lower_site = site.lower()
        metric_handlers[lower_site] = {}
        for genre in genre_to_kind:
            metric_handlers[lower_site][genre] = MetricHandler(genre,
                                                               genre_to_kind[genre],
                                                               lower_site,
                                                               log_to_redis)

    metric_handlers["overall"] = {}
    metric_handlers["overall"]["just_stopstalk_code_time"] = MetricHandler("just_stopstalk_code_time",
                                                                           "average",
                                                                           "overall",
                                                                           log_to_redis)
    return metric_handlers


# ------------------------------------------------------------------------------
def pick_a_problem(user_id, custom=False, **args):
    db = current.db
    ptable = db.problem
    solved_problems, unsolved_problems = get_solved_problems(user_id, custom)

    query = ~ptable.id.belongs(solved_problems.union(unsolved_problems))

    if "kind" not in args:
        args["kind"] = "random"

    if args["kind"] == "random":
        record = db(query).select(ptable.id, orderby="<random>").first()
    elif args["kind"] == "suggested_tag":
        sttable = db.suggested_tags
        ttable = db.tag
        tag_query = (sttable.tag_id == ttable.id) & \
                    (ttable.value == args["tag_category"])
        pids = db(tag_query).select(sttable.problem_id, distinct=True)
        pids = set([x.problem_id for x in pids])
        query &= ptable.id.belongs(pids)
        record = db(query).select(ptable.id, orderby="<random>").first()

    return record.id

# ------------------------------------------------------------------------------
def get_user_record_cache_key(user_id):
    return "auth_user_cache::user_" + str(user_id)

# ------------------------------------------------------------------------------
def get_duration_string(seconds):
    years = seconds / (365 * 24 * 3600)
    days = seconds / (24 * 3600)
    seconds = seconds % (24 * 3600)
    hours = seconds / 3600
    seconds %= 3600
    minutes = seconds / 60
    seconds %= 60

    result = ""
    if years > 0:
        result += " " + str(years) + "y"
    if days > 0:
        result += " " + str(days) + "d"
    if hours > 0:
        result += " " + str(hours) + "h"
    if minutes > 0:
        result += " " + str(minutes) + "m"
    if seconds > 0:
        result += " " + str(seconds) + "s"
    return result.strip()

# ------------------------------------------------------------------------------
def get_user_records(record_values,
                     search_key="id",
                     dict_key="id",
                     just_one_record=False):
    """
        Cache the user records requested in redis if not present and return the
        dictionary of record details based on the dict_key passed as the key

        @param record_values(List): List of values to query with
        @param search_key(String); "id" or "stopstalk_handle"
        @param dict_key(String): "id" or "stopstalk_handle" which will be
                                 used as key in the return value
        @param just_one_record(Boolean): If just return the record value instead
                                         of the key being dict_key

        @return (Storage): Storage dictionary of the record details
    """

    if search_key not in ["id", "stopstalk_handle"] or \
       dict_key not in ["id", "stopstalk_handle"]:
        return None

    def _get_result_key(user_details):
        return user_details[dict_key]

    db = current.db
    atable = db.auth_user

    if search_key == "stopstalk_handle":
        user_ids = db(atable.stopstalk_handle.belongs(record_values)).select(atable.id)
        record_values = [x.id for x in user_ids]
        search_key = "id"

    result = {}
    to_be_fetched = []

    for user_id in record_values:
        redis_key = get_user_record_cache_key(user_id)
        val = current.REDIS_CLIENT.get(redis_key)
        if val is None:
            to_be_fetched.append(user_id)
        else:
            # User details present in redis already
            val = Storage(json.loads(val))
            result[_get_result_key(val)] = val

    records = db(atable.id.belongs(to_be_fetched)).select()
    records = dict([x.id, x.as_json()] for x in records)
    for user_id in records.keys():
        redis_key = get_user_record_cache_key(user_id)
        val = Storage(json.loads(records[user_id]))
        current.REDIS_CLIENT.set(redis_key, records[user_id],
                                 ex=1 * 60 * 60)
        result[_get_result_key(val)] = val

    if just_one_record:
        return result.values()[0] if len(result) else None
    else:
        return result

# ------------------------------------------------------------------------------
def get_boto3_client():
    return client("s3",
                  aws_access_key_id=current.s3_access_key_id,
                  aws_secret_access_key=current.s3_secret_access_key)

# ------------------------------------------------------------------------------
def get_contests():

    cache_value = current.REDIS_CLIENT.get(CONTESTS_CACHE_KEY)
    if cache_value:
        return json.loads(cache_value)

    today = datetime.datetime.today()
    today = datetime.datetime.strptime(str(today)[:-7],
                                       "%Y-%m-%d %H:%M:%S")
    import requests
    from urllib3 import disable_warnings
    disable_warnings()

    response = requests.get("https://kontests.net/api/v1/all",
                            timeout=5,
                            verify=False)

    if response.status_code == 200:
        contest_list = response.json()
        contest_list = sorted(contest_list, key=lambda contest: contest["start_time"])
        current.REDIS_CLIENT.set(CONTESTS_CACHE_KEY,
                                 json.dumps(contest_list),
                                 ex=ONE_HOUR)
        return contest_list
    else:
        return []

# ------------------------------------------------------------------------------
def merge_duplicate_problems(original_id, duplicate_id):
    """
        Merge two duplicate problems and remove the duplicate problem from database

        @param original_id(Integer): problem_id of original problem
        @param duplicate_id(Integer): problem_id of duplicate problem
    """
    if original_id == duplicate_id:
        return


    def _merge_user_ids(original_user_ids, duplicate_user_ids):
        if original_user_ids is None:
            original_user_ids = ""
        if duplicate_user_ids is None:
            duplicate_user_ids = ""
        final_list = list(set(original_user_ids.split(","))
                            .union(set(duplicate_user_ids.split(","))))
        return ",".join(filter(lambda x:  x != "", final_list))

    db = current.db
    ptable = db.problem
    stable = db.submission
    sttable = db.suggested_tags
    uetable = db.user_editorials
    pdtable = db.problem_difficulty

    original_row = ptable(original_id)
    duplicate_row = ptable(duplicate_id)

    # Editorial link -----------------------------------------------------------
    print "---------------------"
    print original_row.editorial_link, duplicate_row.editorial_link
    if original_row.editorial_link in ["", None] and \
       duplicate_row.editorial_link not in ["", None]:
        original_row.update({"editorial_link": duplicate_row.editorial_link})
    print original_row.editorial_link

    # Problem tag --------------------------------------------------------------
    print "---------------------"
    original_tags = eval(original_row.tags) if original_row.tags != "['-']" else []
    print "original_tags", original_tags
    duplicate_tags = eval(duplicate_row.tags) if duplicate_row.tags != "['-']" else []
    print "duplicate_tags", duplicate_tags
    original_tags = list(set(original_tags).union(set(duplicate_tags)))
    if len(original_tags) != 0:
        original_row.update({"tags": str(original_tags)})
    print "final_tags", original_tags

    # Submission table ---------------------------------------------------------
    print "---------------------"
    updated = db(stable.problem_id == duplicate_id).update(problem_id=original_id)
    print "Updated %d submission records" % updated

    # Problem user_ids ---------------------------------------------------------
    original_row.update({
        "user_ids": _merge_user_ids(original_row.user_ids,
                                    duplicate_row.user_ids)
    })
    original_row.update({
        "custom_user_ids": _merge_user_ids(original_row.custom_user_ids,
                                           duplicate_row.custom_user_ids)
    })

    db.commit()

    # total_submissions, solved_submissions ------------------------------------
    srows = db(stable.problem_id == original_id).select(stable.status)
    accepted = len(filter(lambda x: x["status"] == "AC", srows))
    print "---------------------"
    print original_row.solved_submissions, original_row.total_submissions
    print "accepted", accepted, "total_submissions", len(srows)
    original_row.update({"solved_submissions": accepted,
                         "total_submissions": len(srows)})

    # suggested tags -----------------------------------------------------------
    for strow in db(sttable.problem_id == duplicate_id).select():
        query = (sttable.problem_id == original_id) & \
                (sttable.user_id == strow.user_id)
        if db(query).select().first() is None:
            strow.update(problem_id=original_id)
        else:
            strow.delete_record()

    # user editorials ----------------------------------------------------------
    for uerow in db(uetable.problem_id == duplicate_id).select():
        query = (uetable.problem_id == original_id) & \
                (uetable.user_id == uerow.user_id)
        if db(query).select().first() is None:
            uerow.update(problem_id=original_id)
        else:
            uerow.delete_record()

    # problem difficulty -------------------------------------------------------
    for pdrow in db(pdtable.problem_id == duplicate_id).select():
        query = (pdtable.problem_id == original_id) & \
                (pdtable.user_id == pdrow.user_id)
        if db(query).select().first() is None:
            pdrow.update(problem_id=original_id)
        else:
            pdrow.delete_record()

    original_row.update_record()
    duplicate_row.delete_record()

    db.commit()
    return

# -----------------------------------------------------------------------------
def get_solved_problems(user_id, custom=False):
    """
        Get the solved and unsolved problems of a user

        @param user_id(Integer): user_id
        @param custom(Boolean): If the user_id is a custom user
        @return(Tuple): List of solved and unsolved problems
    """

    if user_id is None:
        return None

    def _settify_return_value(data):
        return map(lambda x: set(x), data)

    db = current.db
    stable = db.submission
    stopstalk_handle = get_stopstalk_handle(user_id, custom)
    redis_cache_key = "solved_unsolved_" + stopstalk_handle
    data = current.REDIS_CLIENT.get(redis_cache_key)
    if data:
       return _settify_return_value(json.loads(data))

    base_query = (stable.custom_user_id == user_id) if custom else (stable.user_id == user_id)
    query = base_query & (stable.status == "AC")
    problems = db(query).select(stable.problem_id, distinct=True)
    solved_problems = set([x.problem_id for x in problems])

    query = base_query
    problems = db(query).select(stable.problem_id, distinct=True)
    all_problems = set([x.problem_id for x in problems])
    unsolved_problems = all_problems - solved_problems

    data = [list(solved_problems), list(unsolved_problems)]
    current.REDIS_CLIENT.set(redis_cache_key,
                             json.dumps(data, separators=JSON_DUMP_SEPARATORS),
                             ex=1 * 60 * 60)

    return _settify_return_value(data)

# -----------------------------------------------------------------------------
def get_next_problem_to_suggest(user_id, problem_id=None):
    db = current.db
    pdtable = db.problem_difficulty
    ptable = db.problem
    result = "all_caught"

    if not problem_id:
        solved_problems, unsolved_problems = get_solved_problems(user_id, False)

        query = (pdtable.user_id == user_id)
        existing_pids = db(query).select()
        existing_pids = [x.problem_id for x in existing_pids]

        final_set = solved_problems.union(unsolved_problems) - set(existing_pids)
        if len(final_set) != 0:
            import random
            next_problem_id = random.sample(sorted(list(final_set),
                                                   reverse=True)[:15],
                                            1)[0]
            precord = ptable(next_problem_id)
            result = "success"
        else:
            precord = None
            result = "all_caught"
    else:
        precord = ptable(problem_id)
        result = "success"

    if precord:
        query = (pdtable.user_id == user_id) & \
                (pdtable.problem_id == precord.id)
        pdrecord = db(query).select().first()
        link_class, link_title = get_link_class(precord.id, user_id)
        return dict(result=result,
                    problem_id=precord.id,
                    pname=precord.name,
                    plink=problem_widget(precord.name,
                                         precord.link,
                                         link_class,
                                         link_title,
                                         precord.id,
                                         True,
                                         request_vars={"submission_type": "my"}),
                    score=pdrecord.score if pdrecord else None)
    else:
        return dict(result=result)

# -----------------------------------------------------------------------------
def get_link_class(problem_id, user_id, solved_result=None):
    link_class = "unattempted-problem"
    if user_id is None:
        return link_class, (" ".join(link_class.split("-"))).capitalize()

    if solved_result is None:
        solved_problems, unsolved_problems = get_solved_problems(user_id, False)
    else:
        solved_problems, unsolved_problems = solved_result

    link_class = ""
    if problem_id in unsolved_problems:
        # Checking for unsolved first because most of the problem links
        # would be found here instead of a failed lookup in solved_problems
        link_class = "unsolved-problem"
    elif problem_id in solved_problems:
        link_class = "solved-problem"
    else:
        link_class = "unattempted-problem"

    return link_class, (" ".join(link_class.split("-"))).capitalize()

# -----------------------------------------------------------------------------
def get_stopstalk_handle(user_id, custom):
    """
        Given a user_id (custom/normal), get the stopstalk_handle

        @param user_id (Integer): user_id stopstalk_handle of which needs to be returned
        @param custom (Boolean): If the user_id corresponds to custom_friend table

        @return (String): stopstalk_handle of the user
    """

    table = current.db.custom_friend if custom else current.db.auth_user
    return table(user_id).stopstalk_handle

# -----------------------------------------------------------------------------
def get_rating_information(user_id, custom, is_logged_in):
    db = current.db
    stopstalk_handle = get_stopstalk_handle(user_id, custom)
    redis_cache_key = "profile_page:user_stats_" + stopstalk_handle

    # Check if data is present in REDIS
    data = current.REDIS_CLIENT.get(redis_cache_key)
    if data:
        result = json.loads(data)
        if not is_logged_in and "rating_history" in result:
            del result["rating_history"]
        if "problems_authored_count" not in result:
            result["problems_authored_count"] = 0
        return result

    stable = db.submission

    query = (stable["custom_user_id" if custom else "user_id"] == user_id)
    rows = db(query).select(stable.time_stamp,
                            stable.problem_id,
                            stable.status,
                            stable.site,
                            orderby=stable.time_stamp)

    # Returns rating history, accepted & max streak (day and accepted),
    result = get_stopstalk_user_stats(stopstalk_handle,
                                      custom,
                                      rows.as_list())

    if is_logged_in:
        current.REDIS_CLIENT.set(redis_cache_key,
                                 json.dumps(result, separators=JSON_DUMP_SEPARATORS),
                                 ex=1 * 60 * 60)
    elif "rating_history" in result:
        del result["rating_history"]

    return result
# -----------------------------------------------------------------------------
def handles_updated(record, form):
    """
        Check if any of the handles are updated

        @param record (Row object): Record containing original user details
        @param form (Form object): Form containing values entered by user
        @return (List): The sites corresponding to site handles that are updated
    """
    # List of sites whose site handles are updated
    updated_sites = []
    for site in current.SITES:
        site_handle = site.lower() + "_handle"
        if record[site_handle] != form.vars[site_handle]:
            updated_sites.append(site)
    return updated_sites

# -----------------------------------------------------------------------------
def pretty_string(all_items):
    """
        Helper function to get a valid English statement for a list

        @param all_items (Set): Set of items to be joined into English string
        @return (String): Pretty string
    """
    all_items = list(all_items)
    if len(all_items) == 1:
        return all_items[0]
    else:
        return ", ".join(all_items[:-1]) + " and " + all_items[-1]

# ------------------------------------------------------------------------------
def get_problems_table(all_problems,
                       logged_in_user_id,
                       page_prefix,
                       problem_with_user_editorials=None):
    T = current.T
    db = current.db
    uetable = db.user_editorials
    table = TABLE(_class="bordered centered")
    thead = THEAD(TR(TH(T("Problem Name"), _class=generate_page_specific_class(page_prefix, "name-column")),
                     TH(T("Problem URL")),
                     TH(T("Site")),
                     TH(T("Accuracy")),
                     TH(T("Users solved")),
                     TH(T("Editorial")),
                     TH(T("Tags"), _class="left-align-problem")))

    table.append(thead)
    tbody = TBODY()

    if problem_with_user_editorials is None:
        rows = db(uetable.verification == "accepted").select(uetable.problem_id)
        problem_with_user_editorials = set([x["problem_id"] for x in rows])

    solved_result = get_solved_problems(logged_in_user_id)

    for problem in all_problems:
        tr = TR()

        link_class, link_title = get_link_class(problem["id"],
                                                logged_in_user_id,
                                                solved_result)

        tr.append(TD(problem_widget(problem["name"],
                                    problem["link"],
                                    link_class,
                                    link_title,
                                    problem["id"],
                                    page_prefix=page_prefix),
                     _class=generate_page_specific_class(page_prefix, "name-column")))
        tr.append(TD(A(I(_class="fa fa-link"),
                       _href=problem["link"],
                       _class=generate_page_specific_class(page_prefix, "tag-problem-link") + " tag-problem-link",
                       data={"pid": problem["id"]},
                       _target="_blank")))
        tr.append(TD(IMG(_src=current.get_static_url("images/" + \
                                    urltosite(problem["link"]) + \
                                    "_small.png"),
                         _style="height: 30px; width: 30px;")))
        if problem["solved_submissions"] and problem["total_submissions"]:
            tr.append(TD("%.2f" % (problem["solved_submissions"]  * 100.0 / \
                                   problem["total_submissions"])))
        else:
            tr.append(TD("-"))
        tr.append(TD(problem["user_count"] + problem["custom_user_count"]))

        if problem["id"] in problem_with_user_editorials or \
           problem["editorial_link"] not in ("", None):
            tr.append(TD(A(I(_class="fa fa-book"),
                           _href=URL("problems",
                                     "editorials",
                                     args=problem["id"]),
                           _target="_blank",
                           _class=generate_page_specific_class(page_prefix, "editorial-link"))))
        else:
            tr.append(TD())

        td = TD(_class="left-align-problem")
        all_tags = eval(problem["tags"])
        td.append(SPAN(A(I(_class="fa fa-tag"), " Show Tags",
                         _class="show-recommended-problem-tags chip orange darken-1",
                         data={"tags": json.dumps(all_tags)})))
        tr.append(td)
        tbody.append(tr)

    table.append(tbody)

    return table
# -----------------------------------------------------------------------------
def urltosite(url):
    """
        Helper function to extract site from url

        @param url (String): Site URL
        @return url (String): Site
    """
    import sites
    for site in current.SITES:
        if getattr(sites, site.lower()).Profile.is_valid_url(url):
            return site.lower()

    return "unknown_site"

# -----------------------------------------------------------------------------
def problem_widget(name,
                   link,
                   link_class,
                   link_title,
                   problem_id,
                   disable_todo=False,
                   anchor=True,
                   request_vars={},
                   page_prefix=None):
    """
        Widget to display a problem in UI tables

        @param name (String): Problem name
        @param link (String): Problem link
        @param link_class (String): HTML class to determine solved/unsolved
        @param link_title (String): Link title corresponding to link_class
        @param disable_todo (Boolean): Show / Hide todo button

        @return (DIV)
    """

    problem_div = DIV(_style="display: inline;")
    if anchor:
        problem_div.append(A(name,
                             _href=URL("problems",
                                       "index",
                                       vars=dict(problem_id=problem_id,
                                                 **request_vars),
                                       extension=False),
                             _class=generate_page_specific_class(page_prefix, "problem-listing") + " " + link_class,
                             _title=link_title,
                             _target="_blank",
                             data={"pid": problem_id},
                             extension=False))
    else:
        problem_div.append(SPAN(name,
                                _class=link_class,
                                _title=link_title))

    if current.auth.is_logged_in() and disable_todo is False:
        problem_div.append(SPAN("Add to Todo",
                                _class="chip add-to-todo-list",
                                data={"pid": problem_id}))

    return problem_div

# -----------------------------------------------------------------------------
def get_friends(user_id, custom_list=True):
    """
        Friends of user_id (including custom friends)

        @param user_id (Integer): user_id for which friends need to be returned
        @param custom_list (Boolean): If custom users should be returned
        @return (Tuple): (list of friend_ids, list of custom_friend_ids)
    """

    db = current.db
    cftable = db.custom_friend
    ftable = db.following

    cf_to_duplicate = []
    if custom_list:
        # Retrieve custom friends
        query = (cftable.user_id == user_id)
        custom_friends = db(query).select(cftable.id, cftable.duplicate_cu)
        for custom_friend in custom_friends:
            cf_to_duplicate.append((custom_friend.id,
                                    custom_friend.duplicate_cu))

    # Retrieve friends
    query = (ftable.follower_id == user_id)
    friends = db(query).select(ftable.user_id)
    friends = [x["user_id"] for x in friends]

    return friends, cf_to_duplicate

# ----------------------------------------------------------------------------
def get_stopstalk_rating(parts):
    WEIGHTING_FACTORS = current.WEIGHTING_FACTORS
    rating_components = [
        parts["curr_day_streak"] * WEIGHTING_FACTORS["curr_day_streak"],
        parts["max_day_streak"] * WEIGHTING_FACTORS["max_day_streak"],
        parts["solved"] * WEIGHTING_FACTORS["solved"],
        float("%.2f" % ((parts["accepted_submissions"] * 100.0 / parts["total_submissions"]) * WEIGHTING_FACTORS["accuracy"])),
        (parts["total_submissions"] - parts["accepted_submissions"]) * WEIGHTING_FACTORS["attempted"],
        float("%.2f" % (parts["curr_per_day"] * WEIGHTING_FACTORS["curr_per_day"]))
    ]
    return {"components": rating_components,
            "total": sum(rating_components)}

# ----------------------------------------------------------------------------
def get_country_details(country):
    return [current.all_countries[country], country] if country in current.all_countries else None

# ----------------------------------------------------------------------------
def clear_profile_page_cache(stopstalk_handle):
    """
        Clear all the data in REDIS corresponding to stopstalk_handle
    """
    current.REDIS_CLIENT.delete("handle_details_" + stopstalk_handle)
    current.REDIS_CLIENT.delete("solved_unsolved_" + stopstalk_handle)
    current.REDIS_CLIENT.delete("get_graph_data_" + stopstalk_handle)
    current.REDIS_CLIENT.delete("profile_page:user_stats_" + stopstalk_handle)

# ----------------------------------------------------------------------------
def get_stopstalk_user_stats(stopstalk_handle, custom, user_submissions):

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Initializations
    solved_problem_ids = set([])
    all_attempted_pids = set([])
    problems_authored_count = 0
    sites_solved_count = {}
    site_accuracies = {}
    for site in current.SITES:
        sites_solved_count[site] = set([])
        site_accuracies[site] = {"accepted": 0, "total": 0}

    status_percentages = {}
    final_rating = {}
    calendar_data = {}
    curr_day_streak = max_day_streak = 0
    curr_accepted_streak = max_accepted_streak = 0

    if not custom:
        problems_authored_count = len(get_problems_authored_by(stopstalk_handle))

    if len(user_submissions) == 0:
        return dict(
                    rating_history=[],
                    curr_accepted_streak=0,
                    max_accepted_streak=0,
                    curr_day_streak=0,
                    max_day_streak=0,
                    solved_counts={},
                    status_percentages={},
                    site_accuracies={},
                    solved_problems_count=0,
                    total_problems_count=0,
                    calendar_data={},
                    problems_authored_count=0
                )

    INITIAL_DATE = datetime.datetime.strptime(current.INITIAL_DATE,
                                              "%Y-%m-%d %H:%M:%S").date()
    current_rating_parts = {
        "curr_day_streak": 0,
        "max_day_streak": 0,
        "curr_accepted_streak": 0,
        "max_accepted_streak": 0,
        "solved": 0,
        "total_submissions": 0,
        "current_per_day": 0,
        "accepted_submissions": 0
    }

    first_date = user_submissions[0]["time_stamp"].date()
    date_iterator = INITIAL_DATE
    end_date = datetime.datetime.today().date()
    one_day_delta = datetime.timedelta(days=1)
    submission_iterator = 0

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Populate rating
    def _populate_rating(current_rating_parts, date):
        if current_rating_parts["total_submissions"] == 0:
            return
        current_rating_parts["solved"] = len(solved_problem_ids)
        current_rating_parts["curr_per_day"] = current_rating_parts["total_submissions"] * 1.0 / ((date - INITIAL_DATE).days + 1)
        rating_components = get_stopstalk_rating(current_rating_parts)
        final_rating[str(date)] = rating_components["components"]

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Iterate over the submissions and populate the values
    while date_iterator <= end_date:

        # A day is valid for streak if any non-AC submission on a problem or
        # AC submission on a not-solved problem
        valid_date_for_day_streak = False
        day_submission_count = 0
        statuses_count = {}

        # Iterate over submissions from that day
        while submission_iterator < len(user_submissions) and \
              user_submissions[submission_iterator]["time_stamp"].date() == date_iterator:

            submission = user_submissions[submission_iterator]

            # Count total number of problems with this
            if submission["problem_id"] not in all_attempted_pids:
                all_attempted_pids.add(submission["problem_id"])

            # Count the percentages of each status of the user
            if submission["status"] in status_percentages:
                status_percentages[submission["status"]] += 1
            else:
                status_percentages[submission["status"]] = 1

            if submission["status"] in statuses_count:
                statuses_count[submission["status"]] += 1
            else:
                statuses_count[submission["status"]] = 1

            # Update the total number of submissions per site
            site_accuracies[submission["site"]]["total"] += 1

            # Update total submissions
            current_rating_parts["total_submissions"] += 1

            if submission["status"] == "AC":
                # Update the accepted submissions site-wise
                site_accuracies[submission["site"]]["accepted"] += 1

                # Update the site wise solved count
                sites_solved_count[submission["site"]].add(submission["problem_id"])

                # Update the accepted submissions count and the streak
                current_rating_parts["accepted_submissions"] += 1
                current_rating_parts["curr_accepted_streak"] += 1
                current_rating_parts["max_accepted_streak"] = max(current_rating_parts["curr_accepted_streak"],
                                                                  current_rating_parts["max_accepted_streak"])

                # Reset the day streak if just accepted status on already solved problem
                if submission["problem_id"] not in solved_problem_ids:
                    solved_problem_ids.add(submission["problem_id"])
                    valid_date_for_day_streak |= True
                else:
                    valid_date_for_day_streak |= False
            else:
                valid_date_for_day_streak |= True
                current_rating_parts["curr_accepted_streak"] = 0

            submission_iterator += 1
            day_submission_count += 1

        if (day_submission_count == 0 or \
            valid_date_for_day_streak == False) and \
           current_rating_parts["curr_day_streak"] > 0:
            # Reset streak if no submissions
            current_rating_parts["curr_day_streak"] = 0

        if day_submission_count > 0:
            statuses_count.update({"count": day_submission_count})
            calendar_data[str(date_iterator)] = statuses_count

        if valid_date_for_day_streak:
            current_rating_parts["curr_day_streak"] += 1
            current_rating_parts["max_day_streak"] = max(current_rating_parts["curr_day_streak"],
                                                         current_rating_parts["max_day_streak"])

        # Update the current and max day streaks
        curr_day_streak = current_rating_parts["curr_day_streak"]
        max_day_streak = current_rating_parts["max_day_streak"]

        # Update the current and max accepted streaks
        curr_accepted_streak = current_rating_parts["curr_accepted_streak"]
        max_accepted_streak = current_rating_parts["max_accepted_streak"]

        _populate_rating(current_rating_parts, date_iterator)
        date_iterator += one_day_delta

    for site in current.SITES:
        sites_solved_count[site] = len(sites_solved_count[site])
        if site_accuracies[site]["total"] != 0:
            accepted = site_accuracies[site]["accepted"]
            if accepted == 0:
                site_accuracies[site] = "0"
            else:
                val = (accepted * 100.0 / site_accuracies[site]["total"])
                site_accuracies[site] = str(int(val)) if val == int(val) else "%.2f" % val
        else:
            site_accuracies[site] = "-"

    return dict(
        rating_history=sorted(final_rating.items()),
        curr_accepted_streak=curr_accepted_streak,
        max_accepted_streak=max_accepted_streak,
        curr_day_streak=curr_day_streak,
        max_day_streak=max_day_streak,
        solved_counts=sites_solved_count,
        status_percentages=map(lambda x: (x[1], x[0]),
                               status_percentages.items()),
        site_accuracies=site_accuracies,
        solved_problems_count=len(solved_problem_ids),
        total_problems_count=len(all_attempted_pids),
        calendar_data=calendar_data,
        problems_authored_count=problems_authored_count
    )

# ------------------------------------------------------------------------------
def get_problems_authored_by(stopstalk_handle):
    db = current.db
    atable = db.auth_user
    ptable = db.problem
    pstable = db.problem_setters

    problems = []

    query = (atable.stopstalk_handle == stopstalk_handle) & \
            (atable.blacklisted == False) & \
            (atable.registration_key == "")

    user = db(query).select().first()
    if user is None:
        return problems

    site_to_handle = {}
    for site in current.SITES:
        handle = user[site.lower() + "_handle"]
        if handle:
            site_to_handle[site.lower()] = handle

    records = db(pstable.handle.belongs(site_to_handle.values())).select()
    for record in records:
        problem_record = ptable(record.problem_id)
        site = urltosite(problem_record.link)
        if user[site + "_handle"].lower() == record.handle.lower():
            problems.append(problem_record)

    return problems

# -----------------------------------------------------------------------------
def should_show_stopstalk_ads(page_genre, stopstalk_handle=None):
    return False

    # If user is not logged in
    user_logged_in = current.auth.is_logged_in()
    if not user_logged_in or \
       (page_genre == "profile" and \
        stopstalk_handle is None):
        return True

    if page_genre == "profile":
        # Whitelisted set of stopstalk handles
        starting_regexes = ["17", "18", "19", "20", "21", "22"]
        start_condition = any([stopstalk_handle.startswith(x) for x in starting_regexes])
        return start_condition
    elif not user_logged_in:
        return True
    else:
        return False

# -----------------------------------------------------------------------------
def materialize_form(form, fields):
    """
        Change layout of SQLFORM forms

        @params form (FORM): FORM object representing the form DOM
        @params fields (List): List of fields in the form

        @return (DIV): Materialized form wrapped with a DIV
    """

    form.add_class("form-horizontal center")
    main_div = DIV(_class="center")

    for _, label, controls, field_tooltip in fields:
        curr_div = DIV(_class="row center valign-wrapper")
        input_field = None
        _controls = controls

        try:
            _name = controls.attributes["_name"]
        except:
            _name = ""
        try:
            _type = controls.attributes["_type"]
        except:
            _type = "string"

        try:
            _id = controls.attributes["_id"]
        except:
            _id = ""

        if isinstance(controls, INPUT):
            if _type == "file":
                # Layout for file type inputs
                input_field = DIV(DIV(SPAN("Upload"),
                                      INPUT(_type=_type,
                                            _id=_id),
                                      _class="btn"),
                                  DIV(INPUT(_type="text",
                                            _class="file-path",
                                            _placeholder=label.components[0]),
                                      _class="file-path-wrapper"),
                                  _class="col input-field file-field offset-s2 s8")
            elif _type == "checkbox":
                # Checkbox input field does not require input-field class
                input_field = DIV(_controls, label,
                                  _class="col offset-s2 s8")
        if isinstance(controls, SPAN):
            # Mostly for ids which cannot be edited by user
            _controls = INPUT(_value=controls.components[0],
                              _id=_id,
                              _name=_name,
                              _disabled="disabled")
        elif isinstance(controls, TEXTAREA):
            # Textarea inputs
            try:
                _controls = TEXTAREA(controls.components[0],
                                     _name=_name,
                                     _id=_id,
                                     _class="materialize-textarea text")
            except IndexError:
                _controls = TEXTAREA(_name=_name,
                                     _id=_id,
                                     _class="materialize-textarea text")
        elif isinstance(controls, SELECT):
            # Select inputs
            _controls = SELECT(OPTION(label, _value=""),
                               _name=_name,
                               _class="browser-default",
                               *controls.components[1:])
            # Note now label will be the first element
            # of Select input whose value would be ""
            input_field = DIV(_controls,
                              _class="col offset-s2 s8")
        elif isinstance(controls, A):
            # For the links in the bottom while updating tables like auth_user
            label = ""
        elif isinstance(controls, INPUT) is False:
            # If the values are readonly
            _controls = INPUT(_value=controls,
                              _name=_name,
                              _disabled="")

        if input_field is None:
            input_field = DIV(_controls, label,
                              _class="input-field col offset-s2 s8")
        curr_div.append(input_field)

        if field_tooltip:
            curr_div.append(DIV(I(_class="fa fa-info-circle tooltipped",
                                  data={"position": "top",
                                        "delay": "30",
                                        "tooltip": field_tooltip},
                                  _style="cursor: pointer;"),
                                _class="col s1 valign"))
        main_div.append(curr_div)

    return main_div

# -----------------------------------------------------------------------------
def get_problem_details(problem_id):
    redis_cache_key = "problem_details::" + str(problem_id)
    pdetails = current.REDIS_CLIENT.get(redis_cache_key)
    result = None
    if pdetails is None:
        ptable = current.db.problem
        precord = ptable(problem_id)
        result = {"name": precord.name, "link": precord.link}
        current.REDIS_CLIENT.set(redis_cache_key,
                                 json.dumps(result, separators=JSON_DUMP_SEPARATORS),
                                 ex=1 * 60 * 60)
    else:
        result = json.loads(pdetails)

    return result

# -----------------------------------------------------------------------------
def render_table(submissions, duplicates=[], logged_in_user_id=None):
    """
        Create the HTML table from submissions

        @param submissions (Dict): Dictionary of submissions to display
        @param duplicates (List): List of duplicate user ids
        @param logged_in_user_id (Long/None): User id of the logged in user

        @return (TABLE):  HTML TABLE containing all the submissions
    """

    T = current.T
    status_dict = {"AC": "Accepted",
                   "WA": "Wrong Answer",
                   "TLE": "Time Limit Exceeded",
                   "MLE": "Memory Limit Exceeded",
                   "RE": "Runtime Error",
                   "CE": "Compile Error",
                   "SK": "Skipped",
                   "HCK": "Hacked",
                   "PS": "Partially Solved",
                   "OTH": "Others"}

    table = TABLE(_class="bordered centered submissions-table")
    table.append(THEAD(TR(TH(T("Name")),
                          TH(T("Site Profile")),
                          TH(T("Time of submission")),
                          TH(T("Problem"), _class="left-align-problem"),
                          TH(T("Language")),
                          TH(T("Status")),
                          TH(T("Points")),
                          TH(T("View/Download Code")))))

    tbody = TBODY()
    solved_result = get_solved_problems(logged_in_user_id)
    problem_ids = set([x.problem_id for x in submissions])
    pid_to_record = {}
    for pid in problem_ids:
        pid_to_record[pid] = get_problem_details(pid)

    for submission in submissions:
        span = SPAN()

        if submission.user_id:
            person_id = submission.user_id
        else:
            person_id = submission.custom_user_id

            # Check if the given custom_user is a duplicate
            # We need to do this because there might be a case
            # when a duplicate custom_user is created and then
            # his name or institute is changed
            for duplicate in duplicates:
                if duplicate[1] == person_id and duplicate[0]:
                    person_id = current.db.custom_friend(duplicate[0])
                    break

            span = SPAN(_class="orange tooltipped",
                        data={"position": "right",
                              "delay": "50",
                              "tooltip": T("Custom User")},
                        _style="cursor: pointer; " + \
                                "float:right; " + \
                                "height:10px; " + \
                                "width:10px; " + \
                                "border-radius: 50%;")

        tr = TR()
        append = tr.append
        append(TD(DIV(span,
                      A(person_id.first_name + " " + person_id.last_name,
                        _href=URL("user", "profile",
                                  args=person_id.stopstalk_handle,
                                  extension=False),
                        _class="submission-user-name",
                        _target="_blank"))))
        append(TD(A(IMG(_src=current.get_static_url("images/" + \
                                                    submission.site.lower() + \
                                                    "_small.png"),
                        _style="height: 30px; width: 30px;"),
                    _class="submission-site-profile",
                    _href=get_profile_url(submission.site,
                                          submission.site_handle),
                    _target="_blank")))

        append(TD(submission.time_stamp, _class="stopstalk-timestamp"))

        problem_id = submission.problem_id
        link_class, link_title = get_link_class(problem_id,
                                                logged_in_user_id,
                                                solved_result)

        problem_details = pid_to_record[problem_id]
        append(TD(problem_widget(problem_details["name"],
                                 problem_details["link"],
                                 link_class,
                                 link_title,
                                 submission.problem_id),
                  _class="left-align-problem"))
        append(TD(submission.lang))
        append(TD(IMG(_src=current.get_static_url("images/" + submission.status + ".jpg"),
                      _title=status_dict[submission.status],
                      _alt=status_dict[submission.status],
                      _class="status-icon")))
        append(TD(submission.points))

        if submission.view_link:
            submission_data = {"view-link": submission.view_link,
                               "site": submission.site}
            button_class = "btn waves-light waves-effect"
            if current.auth.is_logged_in():
                if submission.site not in VIEW_ONLY_SUBMISSION_SITES:
                    td = TD(BUTTON(T("View"),
                                   _class="view-submission-button " + button_class,
                                   _style="background-color: #FF5722",
                                   data=submission_data),
                            " ",
                            BUTTON(T("Download"),
                                   _class="download-submission-button " + \
                                          button_class,
                                   _style="background-color: #2196F3",
                                   data=submission_data))
                else:
                    td = TD(A(T("View"),
                              _href=submission.view_link,
                              _class="btn waves-light waves-effect",
                              _style="background-color: #FF5722",
                              _target="_blank"))
                append(td)
            else:
                append(TD(BUTTON(T("View"),
                                 _class="btn tooltipped disabled",
                                 _style="background-color: #FF5722",
                                 data={"position": "bottom",
                                       "delay": "50",
                                       "tooltip": T("Login to View")}),
                          " ",
                          BUTTON(T("Download"),
                                 _class="btn tooltipped disabled",
                                 _style="background-color: #2196F3",
                                 data={"position": "bottom",
                                       "delay": "50",
                                       "tooltip": T("Login to Download")})))
        else:
            append(TD())

        tbody.append(tr)
    table.append(tbody)

    return table


# ------------------------------------------------------------------------------
def get_actual_site(lower_site):
    temp_sites_hash = {}
    for site in current.SITES:
        temp_sites_hash[site.lower()] = site

    return temp_sites_hash[lower_site] if lower_site in temp_sites_hash else lower_site

# ------------------------------------------------------------------------------
def get_profile_url(site, handle):
    """
        Get the link to the site profile of a user

        @params site (String): Name of the site according to current.SITES
        @params handle (String): Handle of the user on that site

        @return (String): URL of the user profile on the site
    """

    if handle == "":
        return "NA"

    site = get_actual_site(site)

    url_mappings = {"CodeChef": "users/",
                    "CodeForces": "profile/",
                    "HackerEarth": "users/",
                    "HackerRank": "",
                    "Spoj": "users/",
                    "Timus": "author.aspx?id=",
                    "AtCoder": "users/"}

    if site == "UVa":
        uvadb = current.uvadb
        utable = uvadb.usernametoid
        row = uvadb(utable.username == handle).select().first()
        if row is None:
            import requests
            response = requests.get("https://uhunt.onlinejudge.org/api/uname2uid/" + handle, verify=False)
            if response.status_code == 200 and response.text != "0":
                utable.insert(username=handle, uva_id=response.text.strip())
                return "https://uhunt.onlinejudge.org/id/" + response.text
            else:
                return "NA"
        else:
            return "https://uhunt.onlinejudge.org/id/" + row.uva_id

    else:
        return "%s%s%s" % (current.SITES[site], url_mappings[site], handle)

# ----------------------------------------------------------------------------
def problem_setters_widget(handles, site):
    """
        Get the UI widget to be shown for problem setters

        @param handles (List of String): Site handles of the problem setters
        @param site (String): Site for which the problem is set

        @return (HTML): HTML to be shown for a problem setter
    """

    # Take only unique problem setters
    handles = set(handles)

    db = current.db
    atable = db.auth_user
    site_column = site.lower() + "_handle"
    query = (atable[site_column].belongs(handles)) & \
            (atable.blacklisted == False)
    rows = db(query).select(atable[site_column],
                            atable.stopstalk_handle)
    mapping = dict([(x[site_column], x.stopstalk_handle) for x in rows])
    html_value = DIV(_style="max-width: 500px; overflow: scroll; height: 45px;")
    for handle in handles:
        if handle in mapping:
            html_value.append(SPAN(A(handle,
                                     _href=URL("user",
                                               "profile",
                                               args=mapping[handle]),
                                     _target="_blank"),
                                   _class="problem-setter-on-stopstalk " + \
                                          "problem-setter-href"))
        elif site != "Timus":
            html_value.append(SPAN(A(handle,
                                     _href=get_profile_url(site, handle),
                                     _target="_blank"),
                                   _class="problem-setter-on-profile-site " + \
                                          "problem-setter-href",
                                   _style="white-space: nowrap;"))
        else:
            html_value.append(SPAN(handle,
                                   _class="problem-setter-text"))

    return html_value

# ----------------------------------------------------------------------------
def get_category_wise_problems(solved_problems, unsolved_problems,
                               user_solved_problems, user_unsolved_problems):
    db = current.db
    solved_ids, unsolved_ids = [], []
    ptable = db.problem
    sttable = db.suggested_tags
    ttable = db.tag
    all_tags = db(ttable).select()
    all_tags = dict([(tag.id, tag.value) for tag in all_tags])

    query = ptable.id.belongs(solved_problems.union(unsolved_problems))
    # id => [problem_link, problem_name, problem_class]
    # problem_class =>
    #    0 (Logged in user has solved the problem)
    #    1 (Logged in user has attemted the problem)
    #    2 (User not logged in or not attempted the problem)
    problem_details = {}
    pids = []
    for problem in db(query).select(ptable.id, ptable.link, ptable.name):
        pids.append(problem.id)

        problem_status = 2
        if problem.id in user_unsolved_problems:
            # Checking for unsolved first because most of the problem links
            # would be found here instead of a failed lookup in solved_problems
            problem_status = 1
        elif problem.id in user_solved_problems:
            problem_status = 0

        problem_details[problem.id] = [problem.link, problem.name, problem_status, problem.id]

        if problem.id in solved_problems:
            solved_ids.append(problem.id)
        else:
            unsolved_ids.append(problem.id)

    problem_tags = {}
    query = (sttable.problem_id.belongs(pids)) & \
            (sttable.user_id == 1)
    for prow in db(query).select(sttable.tag_id, sttable.problem_id):
        if prow.problem_id not in problem_tags:
            problem_tags[prow.problem_id] = set([])
        problem_tags[prow.problem_id].add(prow.tag_id)

    categories = {"Dynamic Programming": set([1]),
                  "Greedy": set([28]),
                  "Strings": set([20]),
                  "Hashing": set([32]),
                  "Bit Manipulation": set([21, 42]),
                  "Trees": set([6, 9, 10, 11, 17, 31]),
                  "Graphs": set([4, 5, 15, 22, 23, 24, 26]),
                  "Algorithms": set([12, 14, 27, 29, 35, 36, 37, 38, 44, 51]),
                  "Data Structures": set([2, 3, 7, 8, 33, 34, 49]),
                  "Math": set([16, 30, 39, 40, 41, 43, 45, 50, 54]),
                  "Implementation": set([13, 18, 19]),
                  "Miscellaneous": set([46, 47, 48, 52])}
    ordered_categories = ["Dynamic Programming",
                          "Greedy",
                          "Strings",
                          "Hashing",
                          "Bit Manipulation",
                          "Trees",
                          "Graphs",
                          "Algorithms",
                          "Data Structures",
                          "Math",
                          "Implementation",
                          "Miscellaneous"]

    displayed_problems = set([])
    def _get_categorized_json(problem_ids):
        result = dict([(category, []) for category in ordered_categories])
        for pid in problem_ids:
            this_category = None
            if pid not in problem_tags:
                this_category = "Miscellaneous"
            else:
                ptags = problem_tags[pid]
                category_found = False
                for category in ordered_categories:
                    if len(categories[category].intersection(ptags)) > 0:
                        this_category = category
                        category_found = True
                        break
                if not category_found:
                    this_category = "Miscellaneous"
            pdetails = problem_details[pid]
            plink, pname, _, _ = pdetails
            psite = urltosite(plink)
            if (pname, psite) not in displayed_problems:
                displayed_problems.add((pname, psite))
                result[this_category].append(problem_details[pid])
        return result

    return _get_categorized_json(solved_ids), _get_categorized_json(unsolved_ids)

# ----------------------------------------------------------------------------
def get_contest_graph_data(user_id, custom):
    import os
    import pickle
    custom = (custom == "True")

    stopstalk_handle = get_stopstalk_handle(user_id, custom)
    redis_cache_key = "get_graph_data_" + stopstalk_handle

    # Check if data is present in REDIS
    data = current.REDIS_CLIENT.get(redis_cache_key)
    if data:
        return json.loads(data)

    file_path = "./applications/%s/graph_data/%s" % (current.request.application,
                                                     user_id)
    if custom:
        file_path += "_custom.pickle"
    else:
        file_path += ".pickle"
    if not os.path.exists(file_path):
        return dict(graphs=[])

    graph_data = pickle.load(open(file_path, "rb"))
    graphs = []
    for site in current.SITES:
        lower_site = site.lower()
        if graph_data.has_key(lower_site + "_data"):
            graphs.extend(graph_data[lower_site + "_data"])
    graphs = filter(lambda x: x["data"] != {}, graphs)
    data = dict(graphs=graphs)
    current.REDIS_CLIENT.set(redis_cache_key,
                             json.dumps(data, separators=JSON_DUMP_SEPARATORS),
                             ex=1 * 60 * 60)
    return data

# ----------------------------------------------------------------------------
def render_user_editorials_table(user_editorials,
                                 user_id=None,
                                 logged_in_user_id=None,
                                 read_editorial_class=""):
    """
        Render User editorials table

        @param user_editorials (Rows): Rows object of the editorials
        @param user_id (Number): For which user is the listing happening
        @param logged_in_user_id (Number): Which use is logged in
        @param read_editorial_class (String): HTML class for GA tracking

        @return (HTML): HTML table representing the user editorials
    """

    db = current.db
    atable = db.auth_user
    ptable = db.problem
    T = current.T

    user_ids = set([x.user_id for x in user_editorials])
    user_mappings = get_user_records(user_ids, "id", "id", False)

    query = (ptable.id.belongs([x.problem_id for x in user_editorials]))
    problem_records = db(query).select(ptable.id, ptable.name, ptable.link)

    precords = {}
    for precord in problem_records:
        precords[precord.id] = {"name": precord.name, "link": precord.link}

    table = TABLE(_class="centered user-editorials-table")

    thead = THEAD(TR(TH(T("Problem"), _class="left-align-problem"),
                     TH(T("Site")),
                     TH(T("Editorial By")),
                     TH(T("Added on")),
                     TH(T("Votes")),
                     TH()))
    tbody = TBODY()
    color_mapping = {"accepted": "green",
                     "rejected": "red",
                     "pending": "blue"}

    solved_result = get_solved_problems(logged_in_user_id)
    for editorial in user_editorials:
        if logged_in_user_id != 1 and user_id != editorial.user_id and editorial.verification != "accepted":
            continue

        user = user_mappings[editorial.user_id]
        record = precords[editorial.problem_id]
        number_of_votes = len(editorial.votes.split(",")) if editorial.votes else 0
        link_class, link_title = get_link_class(editorial.problem_id,
                                                logged_in_user_id,
                                                solved_result)
        tr = TR(TD(problem_widget(record["name"],
                                  record["link"],
                                  link_class,
                                  link_title,
                                  editorial.problem_id),
                   _class="left-align-problem"))

        tr.append(TD(IMG(_src=current.get_static_url("images/" + \
                                                     urltosite(record["link"]) + \
                                                     "_small.png"),
                         _style="height: 30px; width: 30px;")))

        if logged_in_user_id is not None and \
           (editorial.user_id == logged_in_user_id or
            logged_in_user_id == 1):
            tr.append(TD(A(user.first_name + " " + user.last_name,
                         _href=URL("user",
                                   "profile",
                                   args=user.stopstalk_handle)),
                         " ",
                         DIV(editorial.verification.capitalize(),
                             _class="verification-badge " + \
                                    color_mapping[editorial.verification])))
        else:
            tr.append(TD(A(user.first_name + " " + user.last_name,
                           _href=URL("user",
                                     "profile",
                                     args=user.stopstalk_handle))))

        tr.append(TD(editorial.added_on))
        vote_class = ""
        if logged_in_user_id is not None and \
           str(logged_in_user_id) in set(editorial.votes.split(",")):
            vote_class = "red-text"
        tr.append(TD(DIV(SPAN(I(_class="fa fa-heart " + vote_class),
                              _class="love-editorial",
                              data={"id": editorial.id}),
                         " ",
                         DIV(number_of_votes,
                             _class="love-count",
                             _style="margin-left: 5px;"),
                         _style="display: inline-flex;")))

        actions_td = TD(A(I(_class="fa fa-eye fa-2x"),
                          _href=URL("problems",
                                    "read_editorial",
                                    args=editorial.id,
                                    extension=False),
                          _class="btn btn-primary tooltipped " + read_editorial_class,
                          _style="background-color: #13AA5F;",
                          data={"position": "bottom",
                                "delay": 40,
                                "tooltip": T("Read Editorial")}))
        if logged_in_user_id is not None and \
           (user.id == logged_in_user_id or logged_in_user_id == 1) and \
           editorial.verification != "accepted":
            actions_td.append(BUTTON(I(_class="fa fa-trash fa-2x"),
                                     _style="margin-left: 2%;",
                                     _class="btn btn-primary red tooltipped delete-editorial",
                                     data={"position": "bottom",
                                           "delay": 40,
                                           "tooltip": T("Delete Editorial"),
                                           "id": editorial.id}))
        tr.append(actions_td)

        tbody.append(tr)

    table.append(thead)
    table.append(tbody)

    return table

# ----------------------------------------------------------------------------
def generate_page_specific_class(page_prefix, class_name):
    return (page_prefix + "-" + class_name) if page_prefix is not None else class_name

# =============================================================================
