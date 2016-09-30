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

import re
from datetime import datetime
from gluon import current, IMG, DIV, TABLE, THEAD, \
                  TBODY, TR, TH, TD, A, SPAN, INPUT, \
                  TEXTAREA, SELECT, OPTION, URL, BUTTON

# -----------------------------------------------------------------------------
def get_link(site, handle):
    """
        Get the URL of site_handle

        @param site (String): Site name
        @param handle (String): Site handle

        @return (String): User profile for that site
    """

    return current.SITES[site] + handle

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
def urltosite(url):
    """
        Helper function to extract site from url

        @param url (String): Site URL
        @return url (String): Site
    """

    # Note: try/except is not added because this function is not to
    #       be called for invalid problem urls
    site = re.search(r"www\..*?\.com", url).group()

    # Remove www. and .com from the url to get the site
    site = site[4:-4]

    return site

# -----------------------------------------------------------------------------
def get_friends(user_id):
    """
        Friends of user_id (including custom friends)

        @param user_id (Integer): Number
        @return (Tuple): (list of friend_ids, list of custom_friend_ids)
    """

    db = current.db
    cftable = db.custom_friend
    ftable = db.friends

    cf_to_duplicate = []
    # Retrieve custom friends
    query = (cftable.user_id == user_id)
    custom_friends = db(query).select(cftable.id, cftable.duplicate_cu)
    for custom_friend in custom_friends:
        cf_to_duplicate.append((custom_friend.id,
                                custom_friend.duplicate_cu))

    # Retrieve friends
    query = (ftable.user_id == user_id)
    friends = db(query).select(ftable.friend_id)
    friends = [x["friend_id"] for x in friends]

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
        rating = (curr_per_day - per_day) * 100000 + \
                  max_streak * 50 + \
                  solved * 100 + \
                  (solved * 100.0 / total_submissions) * 40 + \
                  (total_submissions - solved) * 10 + \
                  per_day * 150
    rating = int(rating)

    if update_flag:
        record.update_record(prev_rating=record.rating)
    if record.rating != rating:
        rating_diff = rating - int(record.rating)
        table = db.custom_friend if custom else db.auth_user
        # Update the rating ONLY when the function
        # is called by update-leaderboard.py
        query = (table.stopstalk_handle == record.stopstalk_handle)
        db(query).update(per_day=per_day,
                         rating=rating,
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

    for _, label, controls, _ in fields:
        curr_div = DIV(_class="row")
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
            label = ""
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
        main_div.append(curr_div)

    return main_div

# -----------------------------------------------------------------------------
def render_table(submissions, duplicates=[]):
    """
        Create the HTML table from submissions

        @param submissions (Dict): Dictionary of submissions to display
        @param duplicates (List): List of duplicate user ids

        @return (TABLE):  HTML TABLE containing all the submissions
    """

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

    table = TABLE(_class="striped centered")
    table.append(THEAD(TR(TH("User Name"),
                          TH("Site"),
                          TH("Site Handle"),
                          TH("Time of submission"),
                          TH("Problem"),
                          TH("Language"),
                          TH("Status"),
                          TH("Points"),
                          TH("View/Download Code"))))

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
                              "tooltip": "Custom User"},
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
                        _target="_blank"))))
        append(TD(submission.site))
        append(TD(A(submission.site_handle,
                    _href=get_link(submission.site,
                                   submission.site_handle),
                    _target="_blank")))
        append(TD(submission.time_stamp, _class="stopstalk-timestamp"))

        link_class = ""
        plink = submission.problem_link
        if plink_to_class.has_key(plink):
            link_class = plink_to_class[plink]
        else:
            if plink in current.solved_problems:
                link_class = "solved-problem"
            elif plink in current.unsolved_problems:
                link_class = "unsolved-problem"
            else:
                # This will prevent from further lookups
                link_class = "unattempted-problem"
            plink_to_class[plink] = link_class

        link_title = (" ".join(link_class.split("-"))).capitalize()

        append(TD(A(submission.problem_name,
                    _href=URL("problems",
                              "index",
                              vars={"pname": submission.problem_name,
                                    "plink": submission.problem_link},
                              extension=False),
                    _class=link_class,
                    _title=link_title,
                    _target="_blank")))
        append(TD(submission.lang))
        append(TD(IMG(_src=URL("static",
                               "images/" + submission.status + ".jpg",
                               extension=False),
                      _title=status_dict[submission.status],
                      _alt=status_dict[submission.status],
                      _style="height: 25px; width: 25px;")))
        append(TD(submission.points))

        if submission.view_link:
            submission_data = {"view-link": submission.view_link,
                               "site": submission.site}
            button_class = "btn waves-light waves-effect"
            if current.auth.is_logged_in():
                if submission.site != "HackerEarth":
                    td = TD(BUTTON("View",
                                   _class="view-submission-button " + button_class,
                                   _style="background-color: #FF5722",
                                   data=submission_data),
                            " ",
                            BUTTON("Download",
                                   _class="download-submission-button " + \
                                          button_class,
                                   _style="background-color: #2196F3",
                                   data=submission_data))
                else:
                    td = TD(A("View",
                              _href=submission.view_link,
                              _class="btn waves-light waves-effect",
                              _style="background-color: #FF5722",
                              _target="_blank"))
                append(td)
            else:
                append(TD(BUTTON("View",
                                 _class="btn tooltipped disabled",
                                 _style="background-color: #FF5722",
                                 data={"position": "bottom",
                                       "delay": "50",
                                       "tooltip": "Login to View"}),
                          " ",
                          BUTTON("Download",
                                 _class="btn tooltipped disabled",
                                 _style="background-color: #2196F3",
                                 data={"position": "bottom",
                                       "delay": "50",
                                       "tooltip": "Login to Download"})))
        else:
            append(TD())

        tbody.append(tr)
    table.append(tbody)

    return table

# =============================================================================
