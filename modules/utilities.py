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

import re
import datetime
import json
from boto3 import client
from health_metrics import MetricHandler
from gluon import current, IMG, DIV, TABLE, THEAD, HR, H5, \
                  TBODY, TR, TH, TD, A, SPAN, INPUT, I, \
                  TEXTAREA, SELECT, OPTION, URL, BUTTON

# -----------------------------------------------------------------------------
def is_valid_stopstalk_handle(handle):
    try:
        group = re.match("[0-9a-zA-Z_]*", handle).group()
        return group == handle
    except AttributeError:
        return False

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

    return metric_handlers


# -----------------------------------------------------------------------------
def get_boto3_client():
    return client("s3",
                  aws_access_key_id=current.s3_access_key_id,
                  aws_secret_access_key=current.s3_secret_access_key)

# -----------------------------------------------------------------------------
def get_solved_problems(user_id, custom=False):
    """
        Get the solved and unsolved problems of a user

        @param user_id(Integer): user_id
        @param custom(Boolean): If the user_id is a custom user
        @return(Tuple): List of solved and unsolved problems
    """

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
                             json.dumps(data, separators=(",", ":")),
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
                                                   reverse=True)[:30],
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
def get_link_class(problem_id, user_id):
    link_class = "unattempted-problem"
    if user_id is None:
        return link_class, (" ".join(link_class.split("-"))).capitalize()

    solved_problems, unsolved_problems = get_solved_problems(user_id, False)

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

# -----------------------------------------------------------------------------
def urltosite(url):
    """
        Helper function to extract site from url

        @param url (String): Site URL
        @return url (String): Site
    """
    if url.__contains__("uva.onlinejudge.org") or url.__contains__("uhunt.felix-halim.net"):
        return "uva"
    if url.__contains__("acm.timus.ru"):
        return "timus"
    if url.__contains__("codechef.com"):
        return "codechef"
    if url == current.spoj_lambda_url:
        return "spoj"
    # Note: try/except is not added because this function is not to
    #       be called for invalid problem urls
    site = re.search(r"www\..*?\.com", url).group()

    # Remove www. and .com from the url to get the site
    site = site[4:-4]

    return site

# -----------------------------------------------------------------------------
def problem_widget(name,
                   link,
                   link_class,
                   link_title,
                   problem_id,
                   disable_todo=False,
                   anchor=True,
                   request_vars={}):
    """
        Widget to display a problem in UI tables

        @param name (String): Problem name
        @param link (String): Problem link
        @param link_class (String): HTML class to determine solved/unsolved
        @param link_title (String): Link title corresponding to link_class
        @param disable_todo (Boolean): Show / Hide todo button

        @return (DIV)
    """

    problem_div = SPAN()
    if anchor:
        problem_div.append(A(name,
                             _href=URL("problems",
                                       "index",
                                       vars=dict(problem_id=problem_id,
                                                 **request_vars),
                                       extension=False),
                             _class="problem-listing " + link_class,
                             _title=link_title,
                             _target="_blank",
                             extension=False))
    else:
        problem_div.append(SPAN(name,
                                _class=link_class,
                                _title=link_title))

    if current.auth.is_logged_in() and disable_todo is False:
        problem_div.append(I(_class="add-to-todo-list fa fa-check-square-o tooltipped",
                             _style="padding-left: 10px; display: none; cursor: pointer;",
                             data={"position": "right",
                                   "delay": "10",
                                   "tooltip": "Add problem to Todo List",
                                   "pid": problem_id}))

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
def clear_profile_page_cache(stopstalk_handle):
    """
        Clear all the data in REDIS corresponding to stopstalk_handle
    """
    current.REDIS_CLIENT.delete("handle_details_" + stopstalk_handle)
    current.REDIS_CLIENT.delete("solved_unsolved_" + stopstalk_handle)
    current.REDIS_CLIENT.delete("get_graph_data_" + stopstalk_handle)
    current.REDIS_CLIENT.delete("profile_page:user_stats_" + stopstalk_handle)

# ----------------------------------------------------------------------------
def get_stopstalk_user_stats(user_submissions):

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Initializations
    solved_problem_ids = set([])
    all_attempted_pids = set([])
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

    if len(user_submissions) == 0:
        return final_rating

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
        calendar_data=calendar_data
    )

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
                                  _class="col input-field file-field offset-s3 s6")
            elif _type == "checkbox":
                # Checkbox input field does not require input-field class
                input_field = DIV(_controls, label,
                                  _class="col offset-s3 s6")
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
                              _class="col offset-s3 s6")
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
                              _class="input-field col offset-s3 s6")
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
def render_table(submissions, duplicates=[], user_id=None):
    """
        Create the HTML table from submissions

        @param submissions (Dict): Dictionary of submissions to display
        @param duplicates (List): List of duplicate user ids

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
                          TH(T("Problem")),
                          TH(T("Language")),
                          TH(T("Status")),
                          TH(T("Points")),
                          TH(T("View/Download Code")))))

    tbody = TBODY()
    # Dictionary to optimize lookup for solved and unsolved problems
    # Multiple lookups in the main set is bad
    pid_to_class = {}

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

        link_class = ""
        problem_id = submission.problem_id
        if pid_to_class.has_key(problem_id):
            link_class, link_title = pid_to_class[problem_id]
        else:
            link_class, link_title = get_link_class(problem_id, user_id)
            pid_to_class[problem_id] = (link_class, link_title)

        append(TD(problem_widget(submission.problem_name,
                                 submission.problem_link,
                                 link_class,
                                 link_title,
                                 submission.problem_id)))
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
                if submission.site != "HackerEarth":
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

# ----------------------------------------------------------------------------
def render_trending_table(caption, problems, column_name, user_id):
    """
        Create trending table from the rows
    """
    T = current.T

    table = TABLE(_class="bordered centered")
    thead = THEAD(TR(TH(T("Problem")),
                     TH(T("Recent Submissions")),
                     TH(column_name)))
    table.append(thead)
    tbody = TBODY()

    for problem in problems:
        tr = TR()
        link_class, link_title = get_link_class(problem[0], user_id)

        tr.append(TD(problem_widget(problem[1]["name"],
                                    problem[1]["link"],
                                    link_class,
                                    link_title,
                                    problem[0])))
        tr.append(TD(problem[1]["total_submissions"]))
        tr.append(TD(len(problem[1]["users"]) + \
                     len(problem[1]["custom_users"])))
        tbody.append(tr)

    table.append(tbody)
    table = DIV(H5(caption, _class="center"), HR(), table)

    return table

# ----------------------------------------------------------------------------
def compute_trending_table(submissions_list, table_type, user_id=None):
    """
        Create trending table from the rows

        @params submission_list (Rows): Submissions to be considered
        @params table_type (String): friends / global
        @params user_id (Long): ID of signed in user else None
    """

    T = current.T
    if table_type == "friends":
        table_header = T("Trending among friends")
        column_name = T("Friends")
    else:
        table_header = T("Trending Globally")
        column_name = T("Users")

    if len(submissions_list) == 0:
        table = TABLE(_class="bordered centered")
        thead = THEAD(TR(TH(T("Problem")),
                         TH(T("Recent Submissions")),
                         TH(column_name)))
        table.append(thead)
        table.append(TBODY(TR(TD("Not enough data to show", _colspan=3))))
        return table

    # Sort the rows according to the number of users
    # who solved the problem in last PAST_DAYS
    custom_compare = lambda x: (len(x[1]["users"]) + \
                                len(x[1]["custom_users"]),
                                x[1]["total_submissions"])

    problems_dict = {}
    for submission in submissions_list:
        plink = submission.problem_link
        pname = submission.problem_name
        uid = submission.user_id
        cid = submission.custom_user_id
        problem_id = submission.problem_id

        if problem_id not in problems_dict:
            problems_dict[problem_id] = {"name": pname,
                                         "total_submissions": 0,
                                         "users": set([]),
                                         "custom_users": set([]),
                                         "link": plink}

        pdict = problems_dict[problem_id]
        pdict["total_submissions"] += 1
        if uid:
            pdict["users"].add(uid)
        else:
            pdict["custom_users"].add(cid)

    trending_problems = sorted(problems_dict.items(),
                               key=custom_compare,
                               reverse=True)

    return render_trending_table(table_header,
                                 trending_problems[:current.PROBLEMS_PER_PAGE],
                                 column_name,
                                 user_id)

# ----------------------------------------------------------------------------
def get_profile_url(site, handle):
    """
        Get the link to the site profile of a user

        @params site (String): Name of the site according to current.SITES
        @params handle (String): Handle of the user on that site

        @return (String): URL of the user profile on the site
    """

    if handle == "":
        return "NA"

    url_mappings = {"CodeChef": "users/",
                    "CodeForces": "profile/",
                    "HackerEarth": "users/",
                    "HackerRank": "",
                    "Spoj": "users/",
                    "Timus": "author.aspx?id="}

    if site == "UVa":
        uvadb = current.uvadb
        utable = uvadb.usernametoid
        row = uvadb(utable.username == handle).select().first()
        if row is None:
            import requests
            response = requests.get("http://uhunt.felix-halim.net/api/uname2uid/" + handle)
            if response.status_code == 200 and response.text != "0":
                utable.insert(username=handle, uva_id=response.text.strip())
                return "http://uhunt.felix-halim.net/id/" + response.text
            else:
                return "NA"
        else:
            return "http://uhunt.felix-halim.net/id/" + row.uva_id

    else:
        return "%s%s%s" % (current.SITES[site], url_mappings[site], handle)

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
    users = db(atable.id.belongs(user_ids)).select()
    user_mappings = {}
    for user in users:
        user_mappings[user.id] = user

    query = (ptable.id.belongs([x.problem_id for x in user_editorials]))
    problem_records = db(query).select(ptable.id, ptable.name, ptable.link)
    precords = {}
    for precord in problem_records:
        precords[precord.id] = {"name": precord.name, "link": precord.link}

    table = TABLE(_class="centered user-editorials-table")
    thead = THEAD(TR(TH(T("Problem")),
                     TH(T("Editorial By")),
                     TH(T("Added on")),
                     TH(T("Votes")),
                     TH()))
    tbody = TBODY()
    color_mapping = {"accepted": "green",
                     "rejected": "red",
                     "pending": "blue"}

    for editorial in user_editorials:
        if logged_in_user_id != 1 and user_id != editorial.user_id and editorial.verification != "accepted":
            continue

        user = user_mappings[editorial.user_id]
        record = precords[editorial.problem_id]
        number_of_votes = len(editorial.votes.split(",")) if editorial.votes else 0
        link_class, link_title = get_link_class(editorial.problem_id, logged_in_user_id)
        tr = TR(TD(problem_widget(record["name"],
                                  record["link"],
                                  link_class,
                                  link_title,
                                  editorial.problem_id)))

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

# =============================================================================
