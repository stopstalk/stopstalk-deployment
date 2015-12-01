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

from gluon import *
import time
import profilesites as profile
from datetime import datetime, date

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
def get_link(site, handle):
    """
        Get the URL of site_handle
    """

    return current.SITES[site] + handle

# -----------------------------------------------------------------------------
def get_friends(user_id):
    """
        Friends of user_id (including custom friens)

        @Return: (list of friend_ids, list of custom_friend_ids)
    """

    db = current.db
    cftable = db.custom_friend
    atable = db.auth_user
    ftable = db.friends

    # Retrieve custom friends
    query = (cftable.user_id == user_id)
    custom_friends = db(query).select(cftable.id)
    custom_friends = map(lambda x: x["id"], custom_friends)

    # Retrieve friends
    query = (ftable.user_id == atable.id)
    friend_ids = db(atable.id != user_id).select(atable.id, join=ftable.on(query))
    friends = map(lambda x: x["id"], friend_ids)

    return friends, custom_friends

# -----------------------------------------------------------------------------
def materialize_form(form, fields):
    """
        Change layout of SQLFORM forms
    """

    form.add_class("form-horizontal center")
    main_div = DIV(_class="center")

    for id, label, controls, help in fields:
        curr_div = DIV(_class="row")
        input_field = None
        _controls = controls

        try:
            _name = controls.attributes["_name"]
        except KeyError:
            _name = ""
        try:
            _type = controls.attributes["_type"]
        except KeyError:
            _type = "string"

        try:
            _id = controls.attributes["_id"]
        except KeyError:
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
                              _type=_type,
                              _name=_name,
                              _id=_id,
                              _disabled="")
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
                               *controls.components[1:]
                               )
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
                              _type=_type,
                              _disabled="")

        if input_field is None:
            input_field = DIV(_controls, label,
                              _class="input-field col offset-s3 s6")
        curr_div.append(input_field)
        main_div.append(curr_div)

    return main_div

# -----------------------------------------------------------------------------
def render_table(submissions):
    """
        Create the HTML table from submissions
    """

    status_dict = {"AC": "Accepted",
                   "WA": "Wrong Answer",
                   "TLE": "Time Limit Exceeded",
                   "MLE": "Memory Limit Exceeded",
                   "RE": "Runtime Error",
                   "CE": "Compile Error",
                   "SK": "Skipped",
                   "HCK": "Hacked",
                   "OTH": "Others",
                   }

    table = TABLE(_class="striped centered")
    table.append(THEAD(TR(TH("User Name"),
                          TH("Site"),
                          TH("Site Handle"),
                          TH("Time of submission"),
                          TH("Problem"),
                          TH("Language"),
                          TH("Status"),
                          TH("Points"),
                          TH("View Code"))))

    tbody = TBODY()
    for submission in submissions:
        tr = TR()
        append = tr.append

        person_id = submission.custom_user_id
        if submission.user_id:
            person_id = submission.user_id

        append(TD(A(person_id.first_name + " " + person_id.last_name,
                    _href=URL("user", "profile",
                              args=[submission.stopstalk_handle]),
                    _target="_blank")))
        append(TD(submission.site))
        append(TD(A(submission.site_handle,
                    _href=get_link(submission.site,
                                   submission.site_handle),
                    _target="_blank")))
        append(TD(submission.time_stamp))
        append(TD(A(submission.problem_name,
                    _href=URL("problems",
                              "index",
                              vars={"pname": submission.problem_name,
                                    "plink": submission.problem_link}),
                    _target="_blank")))
        append(TD(submission.lang))
        append(TD(IMG(_src=URL("static",
                               "images/" + submission.status + ".jpg"),
                      _title=status_dict[submission.status],
                      _style="height: 25px; width: 25px;")))
        append(TD(submission.points))

        if submission.view_link:
            append(TD(A("View",
                        _href=submission.view_link,
                        _class="btn waves-light waves-effect",
                        _style="background-color: #FF5722",
                        _target="_blank")))
        else:
            append(TD())

        tbody.append(tr)
    table.append(tbody)
    return table

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
def retrieve_submissions(reg_user, custom=False):
    """
        Retrieve submissions that are not already in the database
    """

    db = current.db
    stable = db.submission

    # Start retrieving from this date if user registered the first time
    initial_date = current.INITIAL_DATE
    time_conversion = "%Y-%m-%d %H:%M:%S"
    if custom:
        query = (db.custom_friend.id == reg_user)
        row = db(query).select().first()
        table = db.custom_friend
    else:
        query = (db.auth_user.id == reg_user)
        row = db(query).select().first()
        table = db.auth_user

    last_retrieved = db(query).select(table.last_retrieved).first()

    if last_retrieved:
        last_retrieved = str(last_retrieved.last_retrieved)
    else:
        last_retrieved = initial_date

    last_retrieved = time.strptime(str(last_retrieved), time_conversion)
    list_of_submissions = []

    for site in current.SITES:
        site_handle = row[site.lower() + "_handle"]
        if site_handle:
            P = profile.Profile(site, site_handle)
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

    # Update the last retrieved of the user
    today = datetime.now()
    db(query).update(last_retrieved=today)

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
