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
import datetime
import parsedatetime as pdt
import requests
import utilities
import json

user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36"

# ----------------------------------------------------------------------------
def handle_error():
    """
        Handles errors and shows valid error messages
        Also notifies the admin by an email
    """

    def _get_similar_users(url):

        from difflib import SequenceMatcher
        handle = (url.replace("users", "")
                     .replace("user", "")
                     .replace("profiles", "")
                     .replace("profile", "")
                     .replace("submissions", "")
                     .replace("submission", "")
                     .replace("/", "")
                     .lower())
        atable = db.auth_user
        cftable = db.custom_friend
        prospects = []
        users = db(atable).select(atable.first_name,
                                  atable.last_name,
                                  atable.stopstalk_handle).as_list()
        custom_users = db(cftable).select(cftable.first_name,
                                          cftable.last_name,
                                          cftable.stopstalk_handle).as_list()

        prospects.extend([(x["first_name"],
                           x["last_name"],
                           x["stopstalk_handle"]) for x in users + \
                                                           custom_users])

        similar_users = []
        for prospect in prospects:
            fname, lname, stopstalk_handle = prospect
            diff1 = SequenceMatcher(None, fname.lower(), handle).ratio()
            diff2 = SequenceMatcher(None, lname.lower(), handle).ratio()
            diff3 = SequenceMatcher(None,
                                    stopstalk_handle.lower(),
                                    handle).ratio()
            diff = max(diff1, diff2, diff3)
            if diff >= 0.8:
                similar_users.append(({"stopstalk_handle": stopstalk_handle,
                                       "name": fname + " " + lname},
                                      diff))

        similar_users.sort(key=lambda x: x[1], reverse=True)

        return [x[0] for x in similar_users[:10]]

    def _get_failure_message(ticket):

        from os import path
        from gluon.admin import apath
        from pickle import load

        failure_message = str(session.user_id) + " " if auth.is_logged_in() else ""
        ticket_file_path = "applications/stopstalk/errors/" + \
                           ticket.replace(request.application + "/", "")

        if path.exists(ticket_file_path):
            failure_message += load(open(ticket_file_path, "rb"))["output"]
        else:
            failure_message += "Shouldn't be here"

        return "<html>" + str(A(failure_message,
                                _href=URL("admin", "default", "ticket",
                                          args=ticket,
                                          scheme=True,
                                          host=True))) + "</html>"

    code = request.vars.code
    request_url = request.vars.request_url
    ticket = request.vars.ticket

    # Make sure error url is not current url to avoid infinite loop.
    if code is not None and request_url != request.url:
        # Assign the error status code to the current response
        response.status = int(code)

    error_message = ""
    similar_users = []
    if code == "404":
        similar_users = _get_similar_users(request_url)
        message = request_url + \
                  " " + \
                  str([x["stopstalk_handle"] for x in similar_users])
        error_message = "Not found"
    elif code == "500":
        # Get ticket URL:
        ticket_url = URL("admin", "default", "ticket",
                         args=ticket,
                         scheme=True,
                         host=True)
        message = (str(session.user_id) if auth.is_logged_in() else "") + " " + ticket_url
        error_message = "Internal Server error"
        current.send_mail("raj454raj@gmail.com",
                          "500 occurred",
                          _get_failure_message(ticket),
                          mail_type="admin")
    else:
        message = request.vars.requested_uri if request.vars.requested_uri else request_url
        error_message = "Other error"

    db.http_errors.insert(status_code=int(code),
                          content=message,
                          user_id=session.user_id if auth.is_logged_in() else None)

    return dict(error_message=error_message, similar_users=similar_users)

# ----------------------------------------------------------------------------
def user_editorials():

    uetable = db.user_editorials
    atable = db.auth_user
    ptable = db.problem

    # Get all the problems which do not have an official editorial
    query = (ptable.editorial_link == None) | (ptable.editorial_link == "")
    pids = db(query).select(ptable.id)
    pids = [x.id for x in pids]

    pending_count = 0
    accepted_problem_ids = set([])
    rows = db(uetable).select(orderby=~uetable.id)

    # Rows to show on the leaderboard
    table_rows = []

    # To handle multiple accepted editorials of same user on same problem
    user_id_pid_map = {}

    # To store the user objects who have atleast one accepted editorial
    user_object_map = {}

    for row in rows:

        if row.verification != "accepted":
            if row.verification == "pending":
                pending_count += 1
            continue
        else:
            accepted_problem_ids.add(row.problem_id)

        if user_object_map.has_key(row.user_id) is False:
            # Store the user object for later usage
            user_object_map[row.user_id] = atable(row.user_id)

        if row.problem_id not in pids:
            # This problem has an official editorial - don't count in leaderboard
            continue

        if user_id_pid_map.has_key((row.user_id, row.problem_id)):
            # This is to handle multiple accepted editorials of same user on same problem
            continue

        user_id_pid_map[(row.user_id, row.problem_id)] = row

    # The dictionary to store the count mapping of editorials
    editorial_count_dict = {}
    for key in user_id_pid_map:
        value = user_id_pid_map[key]
        vote_count = 0 if value.votes.strip() == "" else len(value.votes.split(","))
        if editorial_count_dict.has_key(value.user_id):
            update_value = editorial_count_dict[value.user_id]
            update_value["count"] += 1
            update_value["votes"] += vote_count
        else:
            editorial_count_dict[value.user_id] = {"count": 1,
                                                   "votes": vote_count}

    for key in editorial_count_dict:
        user_obj = atable(key)
        table_rows.append([editorial_count_dict[key]["count"],
                           editorial_count_dict[key]["votes"],
                           user_obj.stopstalk_handle,
                           user_obj.first_name + " " + user_obj.last_name])

    table_rows = sorted(table_rows, key=lambda x: (x[0], x[1]), reverse=True)

    # Get recent editorials table
    # ----------------------------

    table = TABLE(_class="centered")
    thead = THEAD(TR(TH(T("Problem")),
                     TH(T("Editorial By")),
                     TH(T("Added on")),
                     TH(T("Votes")),
                     TH()))
    tbody = TBODY()

    user_id = session.user_id if auth.is_logged_in() else None
    table = utilities.render_user_editorials_table(rows[:300],
                                                   user_id,
                                                   user_id,
                                                   "read-editorial-user-editorials-page")

    return dict(table_rows=table_rows[:10],
                recent_editorials_table=table,
                pending_count=pending_count)

# ----------------------------------------------------------------------------
def user_wise_editorials():

    atable = db.auth_user
    uetable = db.user_editorials
    ptable = db.problem

    if len(request.args) == 0:
        session.flash = "Invalid StopStalk Handle"
        redirect(URL("default", "user_editorials"))
        return
    else:
        row = db(atable.stopstalk_handle == request.args[0]).select().first()
        if row is None:
            session.flash = "Invalid StopStalk Handle"
            redirect(URL("default", "user_editorials"))
            return

    user_editorials = db(uetable.user_id == row.id).select(orderby=~uetable.id)

    table = utilities.render_user_editorials_table(user_editorials,
                                                   row.id,
                                                   session.user_id if auth.is_logged_in() else None,
                                                   "read-editorial-user-wise-page")

    return dict(table=table,
                stopstalk_handle=row.stopstalk_handle,
                has_editorials=len(user_editorials) > 0)

# ----------------------------------------------------------------------------
def get_started():
    return dict()

# ----------------------------------------------------------------------------
def retrieval_logic():
    return dict()

# ----------------------------------------------------------------------------
def index():
    """
        The main controller which redirects depending
        on the login status of the user and does some
        extra pre-processing
    """
    # If the user is logged in
    if auth.is_logged_in():
        if session.welcome_shown is None:
            session.flash = T("Welcome StopStalker!!")
        elif response.flash is not None:
            session.flash = response.flash
        redirect(URL("default", "submissions", args=[1]))

    return dict()

# ----------------------------------------------------------------------------
def raj454raj():
    return dict()

# ----------------------------------------------------------------------------
@auth.requires_login()
def todo():

    ptable = db.problem
    tltable = db.todo_list

    res = db(tltable.user_id == session.user_id).select(tltable.problem_link)
    table = TABLE(_class="bordered centered")
    table.append(THEAD(TR(TH(T("Problem")),
                          TH(T("Site")),
                          TH(T("Total submissions")),
                          TH(T("Users solved")),
                          TH(T("Remove")))))

    plinks = [x.problem_link for x in res]
    tbody = TBODY()

    rows = db(ptable.link.belongs(plinks)).select(ptable.id,
                                                  ptable.name,
                                                  ptable.link,
                                                  ptable.total_submissions,
                                                  ptable.user_ids,
                                                  ptable.custom_user_ids)

    def _get_ids(ids):
        ids = ids.split(",")
        return [] if ids[0] == "" else ids

    for row in rows:
        link_class, link_title = utilities.get_link_class(row.id, session.user_id)
        uids, cuids = _get_ids(row.user_ids), _get_ids(row.custom_user_ids)

        tbody.append(TR(TD(utilities.problem_widget(row.name,
                                                    row.link,
                                                    link_class,
                                                    link_title,
                                                    row.id,
                                                    disable_todo=True)),
                        TD(IMG(_src=get_static_url("images/" + \
                                                   utilities.urltosite(row.link) + \
                                                   "_small.png"),
                               _style="height: 30px; weight: 30px;")),
                        TD(row.total_submissions),
                        TD(len(uids) + len(cuids)),
                        TD(I(_class="red-text text-accent-4 fa fa-times remove-from-todo",
                             data={"link": row.link}))))
    table.append(tbody)
    div = DIV(DIV(H2(T("ToDo List")),
                  HR(),
                  BR(),
                  table,
                  BR(),
                  _class="col offset-s2 s8 z-depth-2"),
              _class="row")

    return dict(div=div)

# ----------------------------------------------------------------------------
@auth.requires_login()
def remove_todo():
    plink = request.vars["plink"]
    tltable = db.todo_list

    # Delete from table
    query = (tltable.problem_link == plink) & \
            (tltable.user_id == session.user_id)
    db(query).delete()

# ----------------------------------------------------------------------------
@auth.requires_login()
def job_profile():
    s3_key = "resumes/%0.9d.pdf" % session.user_id

    def _get_response_from_record(record):
        """
            @param record (Row): Row object from resume_data table

            @return (String): JSON dump of the record
        """
        return dict(resume_data_record=json.dumps(dict(
                        can_contact=record.can_contact,
                        contact_number=record.contact_number,
                        expected_salary=record.expected_salary,
                        will_relocate=record.will_relocate,
                        experience=record.experience,
                        fulltime_or_internship=record.fulltime_or_internship.split(","),
                        join_from=str(record.join_from),
                        graduation_year=record.graduation_year,
                        linkedin_profile=record.linkedin_profile,
                        github_profile=record.github_profile
                    )))

    def _upload_resume():
        import os
        import uuid
        random_upload_uuid = uuid.uuid4().hex
        temporary_file = "/tmp/resume_" + random_upload_uuid + ".pdf"

        if request.vars.resume_data_file.filename[-4:] != ".pdf":
            response.flash = "Please upload resume in pdf format"
            return "ERROR"

        try:
            with open(temporary_file, 'wb') as f:
                f.write(request.vars.resume_data_file.file.read())
        except Exception as e:
            response.flash = "Something went wrong!"
            return "ERROR"

        client = utilities.get_boto3_client()
        try:
            client.upload_file(temporary_file,
                               current.s3_bucket,
                               s3_key)
            # Delete the local file
            os.remove(temporary_file)
        except Exception as e:
            response.flash = "Error uploading"
            return "ERROR"

        return "SUCCESS"

    rdtable = db.resume_data
    resume_data_record = db(rdtable.user_id == session.user_id).select().first()
    if request.env.request_method == "GET":
        if resume_data_record:
            return _get_response_from_record(resume_data_record)
        else:
            return dict(resume_data_record={})

    result = _upload_resume()
    if result == "ERROR":
        return dict(resume_data_record={})

    opportunity_type = request.vars.get("resume_data_opportunity_type", "")
    if type(opportunity_type) == list:
        opportunity_type = ",".join(opportunity_type)

    update_params = dict(
        user_id=session.user_id,
        resume_file_s3_path=s3_key,
        will_relocate=request.vars.get("resume_data_will_relocate", "") == "on",
        github_profile=request.vars.get("resume_data_github_profile", ""),
        linkedin_profile=request.vars.get("resume_data_linkedin_profile", ""),
        join_from=request.vars.get("resume_data_join_from", ""),
        graduation_year=request.vars.get("resume_data_graduation_year", ""),
        experience=request.vars.get("resume_data_experience", ""),
        fulltime_or_internship=opportunity_type,
        contact_number=request.vars.get("resume_data_contact_number", ""),
        can_contact=request.vars.get("resume_data_can_contact", "") == "on",
        expected_salary=request.vars.get("resume_data_expected_salary", "")
    )
    if resume_data_record is not None:
        # Update in already existing record
        resume_data_record.update_record(**update_params)
    else:
        rdtable.insert(**update_params)
        resume_data_record = db(rdtable.user_id == session.user_id).select().first()

    response.flash = "Successfully saved your details!"
    return _get_response_from_record(resume_data_record)

# ----------------------------------------------------------------------------
@auth.requires_login()
def notifications():
    """
        Show friends (includes CUSTOM) of the logged-in user on day streak
    """

    # Deprecate this route
    redirect(URL("default", "index"))
    return

    if not auth.is_logged_in():
        redirect(URL("default", "index"))

    ftable = db.following
    atable = db.auth_user
    cftable = db.custom_friend

    # Check for streak of friends on stopstalk
    query = (ftable.follower_id == session.user_id)
    rows = db(query).select(atable.id,
                            atable.first_name,
                            atable.last_name,
                            atable.stopstalk_handle,
                            join=ftable.on(ftable.user_id == atable.id))

    # Will contain list of handles of all the friends along
    # with the Custom Users added by the logged-in user
    handles = []
    complete_dict = {}
    u_ids = []
    cu_ids = []

    for user in rows:
        complete_dict[user.stopstalk_handle] = []
        u_ids.append(str(user.id))
        handles.append((user.stopstalk_handle,
                        user.first_name + " " + user.last_name,
                        user.stopstalk_handle))

    # Check for streak of custom friends
    query = (cftable.user_id == session.user_id)
    rows = db(query).select(cftable.id,
                            cftable.first_name,
                            cftable.last_name,
                            cftable.duplicate_cu,
                            cftable.stopstalk_handle)

    for user in rows:
        name = user.first_name + " " + user.last_name
        actual_handle = user.stopstalk_handle
        stopstalk_handle = user.stopstalk_handle
        cid = user.id

        if user.duplicate_cu:
            cid = user.duplicate_cu
            stopstalk_handle = user.duplicate_cu.stopstalk_handle

        handles.append((stopstalk_handle, name, actual_handle))
        complete_dict[stopstalk_handle] = []
        cu_ids.append(str(cid))

    u_ids = u_ids if len(u_ids) else ["-1"]
    cu_ids = cu_ids if len(cu_ids) else ["-1"]

    # Build the complex SQL query
    sql_query = """
SELECT stopstalk_handle, DATE(time_stamp), COUNT(*) as cnt
FROM submission
WHERE user_id in (%s) OR custom_user_id in (%s)
GROUP BY stopstalk_handle, DATE(submission.time_stamp)
ORDER BY time_stamp;
                """ % (",".join(u_ids), ",".join(cu_ids))

    user_rows = db.executesql(sql_query)
    for user in user_rows:
        if complete_dict[user[0]] != []:
            complete_dict[user[0]].append((user[1], user[2]))
        else:
            complete_dict[user[0]] = [(user[1], user[2])]

    # List of users with non-zero streak
    users_on_day_streak = []

    for handle in handles:
        curr_streak = utilities.get_max_streak(complete_dict[handle[0]])[2]

        # If streak is non-zero append to users_on_streak list
        if curr_streak:
            users_on_day_streak.append((handle, curr_streak))

    # Sort the users on streak by their streak
    users_on_day_streak.sort(key=lambda k: k[1], reverse=True)

    # The table containing users on streak(days)
    streak_table = TABLE(THEAD(TR(TH(STRONG(T("User"))),
                                  TH(STRONG(T("Days"))))),
                         _class="bordered centered")

    tbody = TBODY()

    # Append all the users to the final table
    for users in users_on_day_streak:
        handle = users[0]
        curr_streak = users[1]
        tr = TR(TD((A(handle[1],
                      _href=URL("user", "profile", args=[handle[2]]),
                      _target="_blank"))),
                TD(str(curr_streak) + " ",
                   I(_class="fa fa-bolt",
                     _style="color:red"),
                   _class="center"))
        tbody.append(tr)

    streak_table.append(tbody)
    if len(users_on_day_streak) == 0:
        streak_table = H6(T("No friends on day streak"), _class="center")

    return dict(streak_table=streak_table)

# ----------------------------------------------------------------------------
@auth.requires_login()
def unsubscribe():

    utable = db.unsubscriber
    utable.email.default = session.auth.user.email
    utable.email.writable = False
    utable.time_stamp.readable = False
    utable.time_stamp.writable = False

    form = SQLFORM(utable,
                   submit_button=T("Update Subscription"))

    record = db(utable.email == session.auth.user.email).select().first()
    if record:
        form = SQLFORM(utable,
                       record,
                       showid=False,
                       submit_button=T("Update Subscription"))

    form.vars.time_stamp = datetime.datetime.now()
    if form.process().accepted:
        response.flash = T("Subscription details updated")
        redirect(URL("default", "unsubscribe"))
    elif form.errors:
        response.flash = T("Form has errors")

    return dict(form=form)

# ----------------------------------------------------------------------------
def get_custom_users():
    stopstalk_handle = request.vars["stopstalk_handle"]
    atable = db.auth_user
    cftable = db.custom_friend

    row = db(atable.stopstalk_handle == stopstalk_handle).select().first()
    if row:
        custom_users = db(cftable.user_id == row.id).select()
        table = TABLE(THEAD(TR(TH(T("Name")),
                               TH(T("Site Handles")))),
                      _class="centered")
        tbody = TBODY()
        for user in custom_users:
            tr = TR(TD(A(user.first_name + " " + user.last_name,
                         _href=URL("user", "profile",
                                   args=[user.stopstalk_handle],
                                   extension=False),
                         _class="custom-user-list-name",
                         _target="_blank")))
            td = TD()
            for site in current.SITES:
                if user[site.lower() + "_handle"]:
                    td.append(A(DIV(IMG(_src=get_static_url("images/" + \
                                                            site.lower() + \
                                                            "_logo.png")),
                                    user[site.lower() + "_handle"],
                                    _style="background-color: #e4e4e4; color: black;",
                                    _class="chip"),
                                _href=utilities.get_profile_url(site,
                                                                user[site.lower() + "_handle"]),
                                _class="custom-user-modal-site-profile",
                                _target="_blank"))
            tr.append(td)
            tbody.append(tr)

        table.append(tbody)
        return dict(content=table)
    else:
        return dict(content="Something went wrong")

# ----------------------------------------------------------------------------
def log_contest():
    """
        Logging contests into DB
    """

    pvars = request.post_vars

    if None in (pvars.contest_name,
                pvars.site_name,
                pvars.contest_link,
                pvars.logging_type):
        raise HTTP(400, "Bad Request")
        return

    contest_details = "%s %s %s" % (pvars.contest_name,
                                    pvars.site_name,
                                    pvars.contest_link)

    handle = session.handle if auth.is_logged_in() else "NA"

    db.contest_logging.insert(click_type=pvars.logging_type,
                              contest_details=contest_details,
                              stopstalk_handle=handle,
                              time_stamp=datetime.datetime.now())

# ----------------------------------------------------------------------------
def contests():
    """
        Show the upcoming contests
    """

    today = datetime.datetime.today()
    today = datetime.datetime.strptime(str(today)[:-7],
                                       "%Y-%m-%d %H:%M:%S")

    start_date = today.date()
    end_date = start_date + datetime.timedelta(90)
    site_mapping = {"CODECHEF": "CodeChef",
                    "CODEFORCES": "Codeforces",
                    "HACKERRANK": "HackerRank",
                    "HACKEREARTH": "HackerEarth"}
    url = "https://contesttrackerapi.herokuapp.com/"
    response = requests.get(url)
    if response.status_code == 200:
        response = response.json()["result"]
    else:
        return dict(retrieved=False)

    ongoing = response["ongoing"]
    upcoming = response["upcoming"]
    contests = []
    cal = pdt.Calendar()

    table = TABLE(_class="centered bordered", _id="contests-table")
    thead = THEAD(TR(TH(T("Contest Name")),
                     TH(T("Site")),
                     TH(T("Start")),
                     TH(T("Duration/Ending")),
                     TH(T("Link")),
                     TH(T("Add Reminder"))))
    table.append(thead)
    tbody = TBODY()

    button_class = "btn-floating btn-small accent-4 tooltipped"
    view_link_class = button_class + " green view-contest"
    reminder_class = button_class + " orange set-reminder"
    icon_style = "height: 30px; width: 30px;"
    left_tooltip_attrs = {"position": "left", "delay": "50"}

    for i in ongoing:
        if i["Platform"] not in site_mapping:
            continue

        try:
            endtime = datetime.datetime.strptime(i["EndTime"],
                                                 "%a, %d %b %Y %H:%M")
        except ValueError:
            continue

        tr = TR()
        append = tr.append
        span = SPAN(_class="green tooltipped",
                    data={"position": "right",
                          "delay": "50",
                          "tooltip": "Live Contest"},
                    _style="cursor: pointer;" + \
                           "float:right;" + \
                           "height:10px;" + \
                           "width:10px;" + \
                           "border-radius:50%;")
        append(TD(i["Name"], span))
        append(TD(IMG(_src=get_static_url("images/" + \
                                          str(i["Platform"]).lower() + \
                                          "_small.png"),
                      _title=site_mapping[i["Platform"]],
                      _style=icon_style)))

        append(TD("-"))
        append(TD(str(endtime).replace("-", "/"),
                  _class="contest-end-time"))
        append(TD(A(I(_class="fa fa-external-link-square fa-lg"),
                    _class=view_link_class,
                    _href=i["url"],
                    data=dict(tooltip=T("Contest Link"),
                              **left_tooltip_attrs),
                    _target="_blank")))
        append(TD(BUTTON(I(_class="fa fa-calendar-plus-o"),
                         _class=reminder_class + " disabled",
                         data=dict(tooltip=T("Already started!"),
                                   **left_tooltip_attrs))))
        tbody.append(tr)

    for i in upcoming:

        if i["Platform"] not in site_mapping:
            continue

        start_time = datetime.datetime.strptime(i["StartTime"],
                                                "%a, %d %b %Y %H:%M")
        tr = TR()
        append = tr.append
        append(TD(i["Name"]))
        append(TD(IMG(_src=get_static_url("images/" + \
                                          str(i["Platform"]).lower() + \
                                          "_small.png"),
                      _title=site_mapping[i["Platform"]],
                      _style=icon_style)))

        append(TD(str(start_time), _class="stopstalk-timestamp"))

        duration = i["Duration"]
        duration = duration.replace(" days", "d")
        duration = duration.replace(" day", "d")
        append(TD(duration))
        append(TD(A(I(_class="fa fa-external-link-square fa-lg"),
                    _class=view_link_class,
                    _href=i["url"],
                    data=dict(tooltip=T("Contest Link"),
                              **left_tooltip_attrs),
                    _target="_blank")))
        append(TD(BUTTON(I(_class="fa fa-calendar-plus-o"),
                         _class=reminder_class,
                         data=dict(tooltip=T("Set Reminder to Google Calendar"),
                                   **left_tooltip_attrs))))
        tbody.append(tr)

    table.append(tbody)
    return dict(table=table, upcoming=upcoming, retrieved=True)

# ------------------------------------------------------------------------------
def updates():
  """
      Show the updates and feature additions
  """

  return dict()

# ------------------------------------------------------------------------------
def leaderboard():
    """
        Get a table with users sorted by StopStalk rating
    """

    specific_institute = False
    specific_country = False
    atable = db.auth_user
    cftable = db.custom_friend

    global_leaderboard = False
    if request.vars.has_key("global"):
        if request.vars["global"] == "True":
            global_leaderboard = True
        else:
            if not auth.is_logged_in():
                global_leaderboard = True
                if request.extension == "html":
                    response.flash = T("Login to see Friends Leaderboard")
    else:
        if not auth.is_logged_in():
            global_leaderboard = True

    heading = T("StopStalk Global Leaderboard")
    afields = ["id", "first_name", "last_name", "institute", "stopstalk_rating", "per_day",
               "stopstalk_handle", "stopstalk_prev_rating", "per_day_change", "country"]

    aquery = (atable.id > 0)
    if global_leaderboard is False:
        if auth.is_logged_in():
            heading = T("Friends Leaderboard")
            friends, _ = utilities.get_friends(session.user_id, False)

            # Add logged-in user to leaderboard
            friends.append(session.user_id)
            aquery &= (atable.id.belongs(friends))
        else:
            aquery = False

    # Do not display unverified users in the leaderboard
    aquery &= (atable.registration_key == "")

    if request.vars.has_key("q") and request.vars["q"]:
        from urllib import unquote
        institute = unquote(request.vars["q"])
        specific_institute = True
        heading = "StopStalk Leaderboard - " + institute
        aquery &= (atable.institute == institute)

    if request.vars.has_key("country") and request.vars["country"]:
        country = None
        if request.vars["country"] not in reverse_country_mapping:
            if request.vars["country"] in current.all_countries:
                country = request.vars["country"]
            else:
                session.flash = "Invalid country!"
                redirect(URL("default", "index"))
                return
        else:
            country = reverse_country_mapping[request.vars["country"]]

        heading = "StopStalk Leaderboard - " + country
        specific_country = True
        aquery &= (atable.country == country)

    if request.extension == "html":
        return dict(heading=heading,
                    global_leaderboard=global_leaderboard)

    if global_leaderboard == True and \
       specific_institute == False and \
       specific_country == False:
        user_ratings = current.REDIS_CLIENT.get("global_leaderboard_cache")
        if user_ratings:
            users = json.loads(user_ratings)
            logged_in_row = None
            if auth.is_logged_in():
                logged_in_row = filter(lambda x: x[1] == session.handle, users)
                logged_in_row = None if len(logged_in_row) == 0 else logged_in_row[0]

            return dict(users=users, logged_in_row=logged_in_row)

    reg_users = db(aquery).select(*afields, orderby=~atable.stopstalk_rating)

    reg_user_ids = [x.id for x in reg_users]

    cnt_star = cftable.id.count()
    group_query = cftable.user_id.belongs(reg_user_ids)
    custom_friends_count = db(group_query).select(cftable.user_id,
                                                  cnt_star,
                                                  groupby=cftable.user_id)
    custom_friends_count = dict([(x["custom_friend"]["user_id"],
                                  x["_extra"]["COUNT(custom_friend.id)"]) for x in custom_friends_count])

    users = []
    leaderboard_rank = 1
    logged_in_row = None
    for user in reg_users:
        cf_count = 0
        if user.id in custom_friends_count:
            cf_count = custom_friends_count[user.id]

        country_details = None
        if user.country in current.all_countries:
            country_details = [current.all_countries[user.country], user.country]

        this_row = (user.first_name + " " + user.last_name,
                    user.stopstalk_handle,
                    user.institute,
                    user.stopstalk_rating,
                    float(user.per_day_change),
                    country_details,
                    cf_count,
                    leaderboard_rank)

        if auth.is_logged_in() and session.user_id == user.id:
            logged_in_row = this_row

        users.append(this_row)
        leaderboard_rank += 1

    if global_leaderboard == True and \
       specific_institute == False and \
       specific_country == False:
        current.REDIS_CLIENT.set("global_leaderboard_cache",
                                 json.dumps(users),
                                 ex=1 * 60 * 60)

    return dict(users=users, logged_in_row=logged_in_row)

# ----------------------------------------------------------------------------
def user():
    """
        Use the standard auth for user
    """

    # /default/user/profile will enable users to update email
    # and stopstalk_handle which will lead to issues
    if auth.is_logged_in() and \
       len(request.args) > 0 and \
       request.args[0] == "profile":
        redirect(URL("user", "update_details"))

    return dict(form=auth())

# ----------------------------------------------------------------------------
def filters():
    """
        Apply multiple kind of filters on submissions
    """

    stable = db.submission
    get_vars = request.get_vars
    if len(request.args) == 0:
        page = 1
    else:
        page = int(request.args[0])

    if page > 10 and not auth.is_logged_in():
        session.flash = "Log in to see more submissions"
        redirect(URL("default", "index"))
        return

    if current.REDIS_CLIENT.get("languages_updated_on") is None or \
       (datetime.datetime.now() - \
        datetime.datetime.strptime(current.REDIS_CLIENT.get("languages_updated_on"),
                                   "%Y-%m-%d %H:%M:%S")).days > 0: # Smart ;)
        languages = db(stable).select(stable.lang, distinct=True)
        languages = [x.lang for x in languages]
        submission_languages = ",,".join(languages)
        current.REDIS_CLIENT.set("languages_updated_on",
                                 str(datetime.datetime.now())[:-7])
        current.REDIS_CLIENT.set("submission_languages", submission_languages)
    else:
        languages = current.REDIS_CLIENT.get("submission_languages").split(",,")

    table = None
    global_submissions = False
    if get_vars.has_key("global") and get_vars["global"] == "True":
        global_submissions = True

    # If form is not submitted
    if get_vars == {}:
        return dict(languages=languages,
                    div=DIV(),
                    global_submissions=global_submissions,
                    total_pages=0)

    # If nothing is filled in the form
    # these fields should be passed in
    # the URL with empty value
    compulsory_keys = ["pname", "name", "end_date", "start_date"]
    if set(compulsory_keys).issubset(get_vars.keys()) is False:
        session.flash = T("Invalid URL parameters")
        redirect(URL("default", "filters"))

    # Form has been submitted
    cftable = db.custom_friend
    atable = db.auth_user
    ftable = db.following
    ptable = db.problem
    duplicates = []

    switch = DIV(LABEL(H6(T("Friends' Submissions"),
                          INPUT(_type="checkbox", _id="submission-switch"),
                          SPAN(_class="lever pink accent-3"),
                          T("Global Submissions"))),
                 _class="switch")
    table = TABLE()
    div = TAG[""](H4(T("Recent Submissions")), switch, table)

    if global_submissions is False and not auth.is_logged_in():
        session.flash = T("Login to view Friends' submissions")
        new_vars = request.vars
        new_vars["global"] = True
        redirect(URL("default", "filters",
                     vars=new_vars,
                     args=request.args))

    query = True
    username = get_vars["name"]
    if username != "":
        tmplist = username.split()
        for token in tmplist:
            query &= ((cftable.first_name.contains(token)) | \
                      (cftable.last_name.contains(token)) | \
                      (cftable.stopstalk_handle.contains(token)))

    if global_submissions is False:
        # Retrieve all the custom users created by the logged-in user
        query = (cftable.user_id == session.user_id) & query
    cust_friends = db(query).select(cftable.id, cftable.duplicate_cu)

    # The Original IDs of duplicate custom_friends
    custom_friends = []
    for cus_id in cust_friends:
        if cus_id.duplicate_cu:
            duplicates.append((cus_id.id, cus_id.duplicate_cu))
            custom_friends.append(cus_id.duplicate_cu)
        else:
            custom_friends.append(cus_id.id)

    query = (atable.id > 0)
    # Get the friends of logged in user
    if username != "":
        tmplist = username.split()
        username_query = False
        for token in tmplist:
            username_query |= ((atable.first_name.contains(token)) | \
                               (atable.last_name.contains(token)) | \
                               (atable.stopstalk_handle.contains(token)))
            for site in current.SITES:
                username_query |= (atable[site.lower() + \
                                   "_handle"].contains(token))

        query &= username_query

    # @ToDo: Anyway to use join instead of two such db calls
    possible_users = db(query).select(atable.id)
    possible_users = [x.id for x in possible_users]
    friends = possible_users
    query = (stable.id > 0)
    if global_submissions is False:
        query = (ftable.follower_id == session.user_id) & \
                (ftable.user_id.belongs(possible_users))
        friend_ids = db(query).select(ftable.user_id)
        friends = [x.user_id for x in friend_ids]

        if session.user_id in possible_users:
            # Show submissions of user also
            friends.append(session.user_id)

        # User in one of the friends
        query = (stable.user_id.belongs(friends))
        # User in one of the custom friends
        query |= (stable.custom_user_id.belongs(custom_friends))
    elif global_submissions is True and username != "":
        # User in one of the friends
        query = (stable.user_id.belongs(friends))
        # User in one of the custom friends
        query |= (stable.custom_user_id.belongs(custom_friends))

    start_date = get_vars["start_date"]
    end_date = get_vars["end_date"]
    no_date_filter = False
    if start_date == "" and end_date == "":
        no_date_filter = True

    # Else part ensures that both the dates passed
    # are included in the range
    if start_date == "":
        # If start date is empty start from the INITIAL_DATE
        start_date = current.INITIAL_DATE
    else:
        # Else append starting time for that day
        start_date += " 00:00:00"

    if end_date == "":
        # If end date is empty retrieve all submissions till now(current timestamp)
        # Current date/time
        end_date = str(datetime.datetime.today())
        # Remove the last milliseconds from the timestamp
        end_date = end_date[:-7]
    else:
        # Else append the ending time for that day
        end_date += " 23:59:59"

    datetime_validator = IS_DATETIME(format=T("%Y-%m-%d %H:%M:%S"),
                                     error_message="error")

    # Prevent a spam user | Facepalm :/
    if datetime_validator(start_date)[1] == "error" or \
       datetime_validator(end_date)[1] == "error":
       raise HTTP(400, "Spam user block")
       return

    start_time = time.strptime(start_date, "%Y-%m-%d %H:%M:%S")
    end_time = time.strptime(end_date, "%Y-%m-%d %H:%M:%S")

    if no_date_filter:
        # Do no modifications to the query
        pass
    elif end_time > start_time:
        # Submissions in the the range start_date to end_date
        query &= (stable.time_stamp >= start_date) & \
                 (stable.time_stamp <= end_date)
    else:
        session.flash = T("Start Date greater than End Date")
        redirect(URL("default", "filters"))

    pname = get_vars["pname"]
    # Submissions with problem name containing pname
    if pname != "":
        pids = db(ptable.name.contains(pname)).select(ptable.id)
        pids = [x.id for x in pids]
        query &= (stable.problem_id.belongs(pids))

    # Check if multiple parameters are passed
    def _get_values_list(param_name):

        values_list = []
        if get_vars.has_key(param_name):
            values_list = get_vars[param_name]
            if isinstance(values_list, str) and values_list != "":
                values_list = [values_list]
        elif get_vars.has_key(param_name + "[]"):
            values_list = get_vars[param_name + "[]"]
            if isinstance(values_list, str):
                values_list = [values_list]

        return values_list

    # Submissions from this site
    sites = _get_values_list("site")
    if sites:
        query &= (stable.site.belongs(sites))

    # Submissions with this language
    langs = _get_values_list("language")
    if langs:
        query &= (stable.lang.belongs(langs))

    # Submissions with this status
    statuses = _get_values_list("status")
    if statuses:
        query &= (stable.status.belongs(statuses))

    PER_PAGE = current.PER_PAGE
    # Apply the complex query and sort by time_stamp DESC
    filtered = db(query).select(limitby=((page - 1) * PER_PAGE,
                                         page * PER_PAGE),
                                orderby=~stable.time_stamp)

    total_problems = db(query).count()
    total_pages = total_problems / 100
    if total_problems % 100 == 0:
        total_pages += 1

    if total_pages > 10 and not auth.is_logged_in():
        total_pages = 10

    table = utilities.render_table(filtered, duplicates, session.user_id)
    switch = DIV(LABEL(H6(T("Friends' Submissions"),
                          INPUT(_type="checkbox", _id="submission-switch"),
                          SPAN(_class="lever pink accent-3"),
                          T("Global Submissions"))),
                 _class="switch")
    div = TAG[""](switch, table)

    return dict(languages=languages,
                div=div,
                total_pages=total_pages,
                global_submissions=global_submissions)

# ----------------------------------------------------------------------------
@auth.requires_login()
def mark_friend():
    """
        Add a friend on StopStalk
    """

    if len(request.args) < 1:
        raise HTTP(400, "Bad request")
        return T("Invalid URL")

    ftable = db.following
    try:
        friend_id = long(request.args[0])
    except ValueError:
        raise HTTP(400, "Bad request")
        return T("Invalid user argument!")

    if friend_id != session.user_id:
        query = (ftable.follower_id == session.user_id) & \
                (ftable.user_id == friend_id)
        if db(query).count() != 0:
            raise HTTP(400, "Bad request")
            return T("Already friends !!")
    else:
        raise HTTP(400, "Bad request")
        return T("Invalid user argument!")

    # Insert a tuple of users' id into the following table
    ftable.insert(user_id=friend_id, follower_id=session.user_id)

    trtable = db.todays_requests
    query = (trtable.user_id == friend_id) & \
            (trtable.follower_id == session.user_id)
    row = db(query).select().first()
    if row is None or row.transaction_type != "add":
        db(query).delete()
        if row is None:
            # Use this for sending emails to the users everyday
            db.todays_requests.insert(user_id=friend_id,
                                      follower_id=session.user_id,
                                      transaction_type="add")

    return T("Friend added!")

# ----------------------------------------------------------------------------
@auth.requires_login()
def friends():
    """
        List of friends added by the user and who added the user
    """

    ftable = db.following
    atable = db.auth_user
    query = (ftable.user_id == session.user_id) | \
            (ftable.follower_id == session.user_id)
    rows = db(query).select(ftable.user_id, ftable.follower_id)

    # User IDs who the current user is following
    following = set([])
    # User IDs who are following the current user
    followed_by = set([])
    for row in rows:
        if row.user_id == session.user_id:
            followed_by.add(row.follower_id)
        else:
            following.add(row.user_id)

    def _get_tooltip_data(tooltip, buttontype, user_id):
        """
            Function to return data attributes for the tooltipped buttons
        """
        return dict(position="left",
                    delay="50",
                    tooltip=tooltip,
                    buttontype=buttontype,
                    userid=user_id)

    fields = [atable.id,
              atable.first_name,
              atable.last_name,
              atable.stopstalk_handle]

    query = atable.id.belongs(following)
    following_records = db(query).select(*fields, orderby="<random>")

    thead = THEAD(TR(TH(T("Name")), TH(T("Actions"))))
    table1 = TABLE(thead, _class="bordered centered")
    tbody = TBODY()
    btn_class = "tooltipped btn-floating btn-large waves-effect waves-light"

    for row in following_records:
        tooltip_attrs = [T("Unfriend"), "unfriend", str(row.id)]
        tr = TR(TD(A(row.first_name + " " + row.last_name,
                     _href=URL("user", "profile",
                               args=row.stopstalk_handle,
                               extension=False),
                     _class="friends-name",
                     _target="_blank")),
                TD(BUTTON(I(_class="fa fa-user-times fa-3x"),
                          _class=btn_class + " black friends-unfriend",
                          data=_get_tooltip_data(*tooltip_attrs))))
        tbody.append(tr)
    table1.append(tbody)

    table2 = TABLE(thead, _class="bordered centered")
    tbody = TBODY()
    query = atable.id.belongs(followed_by)
    followed_by_records = db(query).select(*fields, orderby="<random>")
    for row in followed_by_records:
        tr = TR()
        tr.append(TD(A(row.first_name + " " + row.last_name,
                     _href=URL("user", "profile",
                               args=[row.stopstalk_handle],
                               extension=False),
                     _class="friends-name",
                     _target="_blank")))

        tooltip_attrs = [None, None, str(row.id)]
        if row.id in following:
            tooltip_attrs[:2] = T("Unfriend"), "unfriend"
            tr.append(TD(BUTTON(I(_class="fa fa-user-times fa-3x"),
                                _class=btn_class + " black friends-unfriend",
                                data=_get_tooltip_data(*tooltip_attrs))))
        else:
            tooltip_attrs[:2] = T("Add friend"), "add-friend"
            tr.append(TD(BUTTON(I(_class="fa fa-user-plus fa-3x"),
                                _class=btn_class + " green friends-add-friend",
                                data=_get_tooltip_data(*tooltip_attrs))))
        tbody.append(tr)
    table2.append(tbody)
    return dict(table1=table1, table2=table2)

# ----------------------------------------------------------------------------
def search():
    """
        Show the list of registered users
    """

    if request.extension == "html":
        # Get all the list of institutes for the dropdown
        itable = db.institutes
        all_institutes = db(itable).select(itable.name,
                                           orderby=itable.name)
        all_institutes = [x.name.strip("\"") for x in all_institutes]
        all_institutes.append("Other")

        country_name_list = current.all_countries.keys()
        country_name_list.sort()

        return dict(all_institutes=all_institutes,
                    country_name_list=country_name_list)

    atable = db.auth_user
    ftable = db.following
    q = request.get_vars.get("q", None)
    institute = request.get_vars.get("institute", None)
    country = request.get_vars.get("country", None)

    # Build query for searching by first_name, last_name & stopstalk_handle
    query = ((atable.first_name.contains(q)) | \
             (atable.last_name.contains(q)) | \
             (atable.stopstalk_handle.contains(q)))

    # Search by profile site handle
    for site in current.SITES:
        field_name = site.lower() + "_handle"
        query |= (atable[field_name].contains(q))

    if auth.is_logged_in():
        # Don't show the logged in user in the search
        query &= (atable.id != session.user_id)

    # Search by institute (if provided)
    if institute:
        query &= (atable.institute == institute)

    # Search by country (if provided)
    if country:
        query &= (atable.country == country)

    query &= (atable.registration_key == "")

    # Columns of auth_user to be retrieved
    columns = [atable.id,
               atable.first_name,
               atable.last_name,
               atable.stopstalk_handle]

    for site in current.SITES:
        columns.append(atable[site.lower() + "_handle"])

    rows = db(query).select(*columns,
                            orderby=[atable.first_name, atable.last_name])
    table = TABLE(_class="bordered centered")
    tr = TR(TH(T("Name")), TH(T("Site handles")))

    if auth.is_logged_in():
        tr.append(TH(T("Actions")))

    thead = THEAD()
    thead.append(tr)
    table.append(thead)

    tbody = TBODY()

    if auth.is_logged_in():
        query = (ftable.follower_id == session.user_id)
        join_query = (ftable.user_id == atable.id)
        friends = db(query).select(atable.id,
                                   join=ftable.on(join_query))
        friends = set([x["id"] for x in friends])

    def _get_tooltip_data(tooltip, buttontype, user_id):
        """
            Function to return data attributes for the tooltipped buttons
        """
        return dict(position="left",
                    delay="50",
                    tooltip=tooltip,
                    buttontype=buttontype,
                    userid=user_id)

    btn_class = "tooltipped btn-floating btn-large waves-effect waves-light"

    for user in rows:

        tr = TR()
        tr.append(TD(A(user.first_name + " " + user.last_name,
                       _href=URL("user", "profile",
                                 args=[user.stopstalk_handle],
                                 extension=False),
                       _class="search-user-name",
                       _target="_blank")))

        td = TD()

        for site in current.SITES:
            if user[site.lower() + "_handle"]:
              td.append(A(DIV(IMG(_src=get_static_url("images/" + \
                                                      site.lower() + \
                                                      "_logo.png")),
                              user[site.lower() + "_handle"],
                              _style="background-color: #e4e4e4; color: black;",
                              _class="chip"),
                          _href=utilities.get_profile_url(site,
                                                          user[site.lower() + "_handle"]),
                          _class="search-site-profile",
                          _target="_blank"))
        tr.append(td)

        # If user is not logged-in then don't show the buttons
        if auth.is_logged_in() is False:
            tbody.append(tr)
            continue

        # Tooltip data attributes
        tooltip_attrs = [None, None, str(user.id)]

        # Check if the current user is already a friend or not
        if user.id not in friends:
            # Not a friend
            tooltip_attrs[:2] = T("Add friend"), "add-friend"
            tr.append(TD(BUTTON(I(_class="fa fa-user-plus fa-3x"),
                                _class=btn_class + " green search-add-friend",
                                data=_get_tooltip_data(*tooltip_attrs))))
        else:
            # Already friends
            tooltip_attrs[:2] = T("Unfriend"), "unfriend"
            tr.append(TD(BUTTON(I(_class="fa fa-user-times fa-3x"),
                                _class=btn_class + " black search-unfriend",
                                data=_get_tooltip_data(*tooltip_attrs))))
        tbody.append(tr)

    table.append(tbody)
    return dict(table=table)

# ----------------------------------------------------------------------------
@auth.requires_login()
def download_submission():
    """
        Return the downloaded submission as a string
    """

    import sites

    site = request.get_vars["site"]
    view_link = request.get_vars["viewLink"]
    if site == "CodeChef":
        return getattr(sites, "codechef").Profile.download_submission(view_link)
    elif site == "CodeForces":
        return getattr(sites, "codeforces").Profile.download_submission(view_link)
    else:
        return -1

# ----------------------------------------------------------------------------
@auth.requires_login()
def unfriend():
    """
        Unfriend the user
    """

    def _invalid_url():
        raise HTTP(400, "Bad request")
        return T("Invalid url arguments")

    if len(request.args) != 1:
        return _invalid_url()
    else:
        try:
            friend_id = long(request.args[0])
        except ValueError:
            return _invalid_url()

        user_id = session.user_id
        ftable = db.following

        # Delete records in the friends table
        query = (ftable.user_id == friend_id) & (ftable.follower_id == user_id)
        if db(query).count() == 0:
            return _invalid_url()

        db(query).delete()

        trtable = db.todays_requests
        query = (trtable.user_id == friend_id) & \
                (trtable.follower_id == session.user_id)
        row = db(query).select().first()
        if row is None or row.transaction_type != "unfriend":
            db(query).delete()
            if row is None:
                # This is to avoid the cases when add-friend button is clicked
                # twice. We don't want the user to get notified if some user
                # added and then unfriended him/her on the same day

                # Use this for sending emails to the users everyday
                db.todays_requests.insert(user_id=friend_id,
                                          follower_id=session.user_id,
                                          transaction_type="unfriend")

        return T("Successfully unfriended")

# ----------------------------------------------------------------------------
@auth.requires_login()
def submissions():
    """
        Retrieve submissions of the logged-in user
    """

    if len(request.args) == 0:
        active = 1
    else:
        try:
            active = int(request.args[0])
        except ValueError:
            # The pagination page number is not integer
            raise HTTP(404)
            return
    session.welcome_shown = True

    cftable = db.custom_friend
    stable = db.submission
    atable = db.auth_user
    ptable = db.problem
    ratable = db.recent_announcements

    # Get all the friends/custom friends of the logged-in user
    friends, cusfriends = utilities.get_friends(session.user_id)

    # The Original IDs of duplicate custom_friends
    custom_friends = []
    for cus_id in cusfriends:
        if cus_id[1] is None:
            custom_friends.append(cus_id[0])
        else:
            custom_friends.append(cus_id[1])

    query = (stable.user_id.belongs(friends)) | \
            (stable.custom_user_id.belongs(custom_friends))

    PER_PAGE = current.PER_PAGE

    if request.extension == "json":
        total_count = db(query).count()
        count = total_count / PER_PAGE
        if total_count % PER_PAGE:
            count += 1

        return dict(count=count,
                    total_rows=1)

    rarecord = db(ratable.user_id == session.user_id).select().first()
    if rarecord is None:
        ratable.insert(user_id=session.user_id)
        rarecord = db(ratable.user_id == session.user_id).select().first()

    user = session.auth.user
    db.sessions_today.insert(message="%s %s %d %s" % (user.first_name,
                                                      user.last_name,
                                                      user.id,
                                                      datetime.datetime.now()))

    offset = PER_PAGE * (active - 1)
    # Retrieve only some number of submissions from the offset
    rows = db(query).select(orderby=~db.submission.time_stamp,
                            limitby=(offset, offset + PER_PAGE))

    table = utilities.render_table(rows, cusfriends, session.user_id)

    country_value = session.auth.user.get("country")
    country = country_value if country_value else "not-available"

    country_form = None
    if country == "not-available":
        country_form = SQLFORM(db.auth_user,
                               session.auth.user,
                               fields=["country"],
                               showid=False)
        if country_form.process(onvalidation=current.sanitize_fields).accepted:
            session.auth.user = db.auth_user(session.user_id)
            session.flash = T("Country updated!")
            redirect(URL("default", "submissions", args=1))
        elif country_form.errors:
            response.flash = T("Form has errors")

    return dict(table=table,
                friends=friends,
                cusfriends=cusfriends,
                total_rows=len(rows),
                country=country,
                country_form=country_form,
                utilities=utilities,
                recent_announcements=json.loads(rarecord.data))

# ----------------------------------------------------------------------------
def faq():
    """
        FAQ page
    """

    div = DIV(_class="row")
    ul = UL(_class="collapsible col offset-s3 s6",
            data={"collapsible": "expandable"})

    faqs = db(db.faq).select()
    for i in xrange(len(faqs)):
        li = LI(DIV(B(str(i + 1) + ". " + faqs[i].question),
                    _class="collapsible-header"),
                DIV(MARKMIN(faqs[i].answer),
                    _class="collapsible-body"))
        ul.append(li)

    div.append(ul)

    return dict(div=div)

# ----------------------------------------------------------------------------
def contact_us():
    """
        Contact Us page
    """

    ctable = db.contact_us

    form = SQLFORM(ctable)

    if auth.is_logged_in():
        user = session.auth.user
        ctable.email.default = user.email

    if form.process().accepted:
        session.flash = T("We will get back to you!")
        current.send_mail(to="contactstopstalk@gmail.com",
                          subject=form.vars.subject,
                          message="From: %s (%s - %s)\n" % \
                                    (form.vars.name,
                                     form.vars.email,
                                     form.vars.phone_number) + \
                                  "Subject: %s\n" % form.vars.subject + \
                                  "Message: %s\n" % form.vars.text_message,
                          mail_type="admin")
        redirect(URL("default", "index"))
    elif form.errors:
        response.flash = T("Please fill all the fields!")

    return dict(form=form)

# ----------------------------------------------------------------------------
def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()

# ==============================================================================
