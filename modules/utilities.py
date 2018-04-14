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

import re
from boto3 import client
from datetime import datetime
from gluon import current, IMG, DIV, TABLE, THEAD, HR, H5, \
                  TBODY, TR, TH, TD, A, SPAN, INPUT, I, \
                  TEXTAREA, SELECT, OPTION, URL, BUTTON

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
    db = current.db
    stable = db.submission

    base_query = (stable.custom_user_id == user_id) if custom else (stable.user_id == user_id)
    query = base_query & (stable.status == "AC")
    problems = db(query).select(stable.problem_link, distinct=True)
    solved_problems = set([x.problem_link for x in problems])

    query = base_query
    problems = db(query).select(stable.problem_link, distinct=True)
    all_problems = set([x.problem_link for x in problems])
    unsolved_problems = all_problems - solved_problems

    return solved_problems, unsolved_problems

# -----------------------------------------------------------------------------
def get_link_class(problem_link, user_id):
    if user_id is None:
        return "unattempted-problem"

    solved_problems, unsolved_problems = get_solved_problems(user_id, False)

    link_class = ""
    if problem_link in unsolved_problems:
        # Checking for unsolved first because most of the problem links
        # would be found here instead of a failed lookup in solved_problems
        link_class = "unsolved-problem"
    elif problem_link in solved_problems:
        link_class = "solved-problem"
    else:
        link_class = "unattempted-problem"

    return link_class

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

    if url.__contains__("uva.onlinejudge.org"):
        return "uva"
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
                   disable_todo=False,
                   anchor=True):
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
                                       vars={"pname": name,
                                             "plink": link},
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
                                   "tooltip": "Add problem to Todo List"}))

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
def get_accepted_streak(user_id, custom):
    """
        Function that returns current streak of accepted solutions

        @param user_id (Integer): user_id or custom_user_id
        @param custom (Boolean): custom user or not

        @return (Integer): Accepted Streak of the user
    """

    if custom:
        attribute = "submission.custom_user_id"
    else:
        attribute = "submission.user_id"

    db = current.db
    sql_query = """
                    SELECT COUNT( * )
                    FROM  `submission`
                    WHERE %s=%d
                    AND time_stamp > (SELECT time_stamp
                                        FROM  `submission`
                                        WHERE %s=%d
                                          AND STATUS <>  'AC'
                                        ORDER BY time_stamp DESC
                                        LIMIT 1);
                """ % (attribute, user_id, attribute, user_id)

    streak = db.executesql(sql_query)
    return streak[0][0]

# ----------------------------------------------------------------------------
def get_max_accepted_streak(user_id, custom):
    """
        Return the max accepted solution streak

        @param user_id (Integer): user_id or custom_user_id
        @param custom (Boolean): custom user or not

        @return (Integer): Maximum Accepted Streak of the user
    """

    if custom:
        attribute = "submission.custom_user_id"
    else:
        attribute = "submission.user_id"

    db = current.db
    sql_query = """
                    SELECT status
                    FROM `submission`
                    WHERE %s=%d
                    ORDER BY time_stamp;
                """ % (attribute, user_id)
    rows = db.executesql(sql_query)

    prev = None
    streak = max_streak = 0

    for status in rows:
        if prev is None:
            streak = 1 if status[0] == "AC" else 0
        elif prev == "AC" and status[0] == "AC":
            streak += 1
        elif prev != "AC" and status[0] == "AC":
            streak = 1
        elif prev == "AC" and status[0] != "AC":
            max_streak = max(max_streak, streak)
            streak = 0
        prev = status[0]

    return max(max_streak, streak)

# ----------------------------------------------------------------------------
def get_max_streak(submissions):
    """
        Get the maximum of all streaks

        @param submissions (List of tuples): [(DateTime object, count)...]
        @return (Tuple): Returns streaks of the user
    """

    streak = 0
    max_streak = 0
    prev = curr = None
    total_submissions = 0

    for i in submissions:
        total_submissions += i[1]
        if prev is None and streak == 0:
            prev = i[0]
            streak = 1
        else:
            curr = i[0]
            if (curr - prev).days == 1:
                streak += 1
            elif curr != prev:
                streak = 1

            prev = curr

        if streak > max_streak:
            max_streak = streak

    today = datetime.today().date()

    # There are no submissions in the database for this user
    if prev is None:
        return (0,) * 4

    # Check if the last streak is continued till today
    if (today - prev).days > 1:
        streak = 0

    return max_streak, total_submissions, streak, len(submissions)

# ----------------------------------------------------------------------------
def compute_row(record,
                complete_dict,
                solved,
                custom=False,
                update_flag=False):
    """
        Computes rating and retrieves other
        information of the specified user

        @param record (Row): User record
        @param complete_dict (Dict): Dict containing daywise count of submissions
        @param solved (Integer): Count of problems solved
        @param custom (Boolean): Custom user or not
        @param update_flag (Boolean): Update db rating

        @return (Tuple): Tuple of details required for leaderboard
    """

    db = current.db
    cftable = db.custom_friend

    stopstalk_handle = record.stopstalk_handle
    if custom:
        if record.duplicate_cu:
            stopstalk_handle = cftable(record.duplicate_cu).stopstalk_handle

    try:
        tup = get_max_streak(complete_dict[stopstalk_handle])
    except KeyError:
        # No submissions corresponding to that user
        tup = get_max_streak([])
    max_streak = tup[0]
    total_submissions = tup[1]

    today = datetime.today().date()
    start = datetime.strptime(current.INITIAL_DATE,
                              "%Y-%m-%d %H:%M:%S").date()

    if record.per_day is None or record.per_day == 0.0:
        per_day = total_submissions * 1.0 / (today - start).days
    else:
        per_day = record.per_day

    curr_per_day = total_submissions * 1.0 / (today - start).days
    diff = "%0.5f" % (curr_per_day - per_day)
    diff = float(diff)

    # I am not crazy. This is to solve the problem
    # if diff is -0.0
    if diff == 0.0:
        diff = 0.0

    if total_submissions == 0:
        rating = 0
    else:
        # Unique rating formula
        # @ToDo: Improvement is always better
        rating = max_streak * 50 + \
                 solved * 100 + \
                 (solved * 100.0 / total_submissions) * 80 + \
                 (total_submissions - solved) * 20 + \
                 per_day * 2000
    rating = int(rating)

    if update_flag:
        record.update_record(stopstalk_prev_rating=record.stopstalk_rating)
    if record.stopstalk_rating != rating:
        rating_diff = rating - record.stopstalk_rating
        table = db.custom_friend if custom else db.auth_user
        # Update the rating ONLY when the function
        # is called by update-leaderboard.py
        query = (table.stopstalk_handle == record.stopstalk_handle)
        db(query).update(per_day=per_day,
                         stopstalk_rating=rating,
                         per_day_change=str(diff))
    else:
        rating_diff = 0

    return (record.first_name + " " + record.last_name,
            record.stopstalk_handle,
            record.institute,
            rating,
            diff,
            custom,
            rating_diff)

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
    plink_to_class = {}

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
                    _href=current.get_profile_url(submission.site,
                                                  submission.site_handle),
                    _target="_blank")))

        append(TD(submission.time_stamp, _class="stopstalk-timestamp"))

        link_class = ""
        plink = submission.problem_link
        if plink_to_class.has_key(plink):
            link_class = plink_to_class[plink]
        else:
            link_class = get_link_class(plink, user_id)
            plink_to_class[plink] = link_class

        link_title = (" ".join(link_class.split("-"))).capitalize()

        append(TD(problem_widget(submission.problem_name,
                                 submission.problem_link,
                                 link_class,
                                 link_title)))
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
        link_class = get_link_class(problem[0], user_id)
        link_title = (" ".join(link_class.split("-"))).capitalize()

        tr.append(TD(problem_widget(problem[1]["name"],
                                    problem[0],
                                    link_class,
                                    link_title)))
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

        if plink not in problems_dict:
            problems_dict[plink] = {"name": pname,
                                    "total_submissions": 0,
                                    "users": set([]),
                                    "custom_users": set([])}

        pdict = problems_dict[plink]
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

# =============================================================================
