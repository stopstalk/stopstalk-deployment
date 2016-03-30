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
import datetime
import parsedatetime as pdt
import requests
from operator import itemgetter
import utilities

# ----------------------------------------------------------------------------
def index():
    """
        The main controller which redirects depending
        on the login status of the user and does some
        extra pre-processing
    """

    # If the user is logged in
    if session["auth"]:
        session.flash = "Welcome StopStalker!!"
        redirect(URL("default", "submissions", args=[1]))

    return dict()

# ----------------------------------------------------------------------------
@auth.requires_login()
def notifications():
    """
        Check if any of the friends(includes CUSTOM) of
        the logged-in user is on a streak
    """

    if session["user_id"] is None:
        redirect(URL("default", "index"))

    ftable = db.friends
    atable = db.auth_user
    cftable = db.custom_friend

    # Check for streak of friends on stopstalk
    query = (ftable.user_id == session["user_id"])
    rows = db(query).select(atable.first_name,
                            atable.last_name,
                            atable.stopstalk_handle,
                            join=ftable.on(ftable.friend_id == atable.id))

    # Will contain list of handles of all the friends along
    # with the Custom Users added by the logged-in user
    handles = []

    for user in rows:
        handles.append((user.stopstalk_handle,
                        user.first_name + " " + user.last_name,
                        user.stopstalk_handle))

    # Check for streak of custom friends
    query = (cftable.user_id == session["user_id"])
    rows = db(query).select(cftable.first_name,
                            cftable.last_name,
                            cftable.duplicate_cu,
                            cftable.stopstalk_handle)
    for user in rows:
        name = user.first_name + " " + user.last_name
        actual_handle = user.stopstalk_handle

        if user.duplicate_cu:
            stopstalk_handle = user.duplicate_cu.stopstalk_handle
        else:
            stopstalk_handle = user.stopstalk_handle

        handles.append((stopstalk_handle, name, actual_handle))

    # List of users with non-zero streak
    users_on_day_streak = []
    users_on_submission_streak = []

    for handle in handles:
        curr_streak = utilities.get_max_streak(handle[0])[2]
        curr_accepted_streak = utilities.get_accepted_streak(handle[0])

        # If streak is non-zero append to users_on_streak list
        if curr_streak:
            users_on_day_streak.append((handle, curr_streak))
        if curr_accepted_streak:
            users_on_submission_streak.append((handle, curr_accepted_streak))

    # Sort the users on streak by their streak
    users_on_day_streak.sort(key=lambda k: k[1], reverse=True)
    users_on_submission_streak.sort(key=lambda k: k[1], reverse=True)

    # The table containing users on streak(days)
    table1 = TABLE(THEAD(TR(TH(STRONG("User")),
                            TH(STRONG("Days")))),
                   _class="col offset-s3 s6 striped centered")

    # The table containing users on streak(submissions)
    table2 = TABLE(THEAD(TR(TH(STRONG("User")),
                            TH(STRONG("Submissions")))),
                   _class="col offset-s3 s6 striped centered")

    tbody1 = TBODY()
    tbody2 = TBODY()

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
        tbody1.append(tr)

    table1.append(tbody1)
    if len(users_on_day_streak) == 0:
        table1 = H6("No friends on day streak", _class="center")

    # Append all the users to the final table
    for users in users_on_submission_streak:
        handle = users[0]
        curr_accepted_streak = users[1]
        tr = TR(TD((A(handle[1],
                      _href=URL("user", "profile", args=[handle[2]]),
                      _target="_blank"))),
                TD(str(curr_accepted_streak) + " ",
                   I(_class="fa fa-bolt",
                     _style="color:red"),
                   _class="center"))
        tbody2.append(tr)

    table2.append(tbody2)
    if len(users_on_submission_streak) == 0:
        table2 = H6("No friends on submission streak", _class="center")

    return dict(table1=table1,
                table2=table2)

# ----------------------------------------------------------------------------
def sort_contests(a, b):
    if a["has_started"] and b["has_started"]:
        return a["end"] < b["end"]
    elif a["has_started"] and b["has_started"] == False:
        return False
    elif a["has_started"] == False and b["has_started"]:
        return True
    else:
        return a["start"] < b["start"]

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
    url = "https://contesttrackerapi.herokuapp.com/"
    response = requests.get(url)
    if response.status_code == 200:
        response = response.json()["result"]
    else:
        # @todo: something better
        return dict()

    ongoing = response["ongoing"]
    upcoming = response["upcoming"]
    contests = []
    cal = pdt.Calendar()

    table = TABLE(_class="centered striped")
    thead = THEAD(TR(TH("Contest Name"),
                     TH("Site"),
                     TH("Start"),
                     TH("Duration/Ending"),
                     TH("Link"),
                     TH("Add Reminder")))
    table.append(thead)
    tbody = TBODY()

    for i in ongoing:

        if i["Platform"] in ("TOPCODER", "OTHER"):
            continue

        try:
            endtime = datetime.datetime.strptime(i["EndTime"],
                                                 "%a, %d %b %Y %H:%M")
        except ValueError:
            continue
        tr = TR()
        span = SPAN(_class="green tooltipped",
                    data={"position": "right",
                          "delay": "50",
                          "tooltip": "Live Contest"},
                    _style="cursor: pointer; " + \
                            "float:right; " + \
                            "height:10px; " + \
                            "width:10px; " + \
                            "border-radius: 50%;")
        tr.append(TD(i["Name"], span))
        tr.append(TD(i["Platform"].capitalize()))
        tr.append(TD("-"))
        tr.append(TD(str(endtime),
                     _class="contest-end-time"))
        tr.append(TD(A(I(_class="fa fa-external-link-square fa-lg"),
                       _class="btn-floating btn-small green accent-4 tooltipped",
                       _href=i["url"],
                       data={"position": "left",
                             "tooltip": "Contest Link",
                             "delay": "50"},
                       _target="_blank")))
        tr.append(TD(BUTTON(I(_class="fa fa-calendar-plus-o"),
                            _class="btn-floating btn-small orange accent-4 tooltipped disabled",
                            data={"position": "left",
                                  "tooltip": "Already started!",
                                  "delay": "50"})))
        tbody.append(tr)

    # This id is used for uniquely identifying
    # a particular contest in js
    button_id = 1
    for i in upcoming:

        if i["Platform"] in ("TOPCODER", "OTHER"):
            continue

        start_time = datetime.datetime.strptime(i["StartTime"],
                                                "%a, %d %b %Y %H:%M")
        tr = TR(_id="contest-" + str(button_id))
        tr.append(TD(i["Name"]))
        tr.append(TD(i["Platform"].capitalize()))
        tr.append(TD(str(start_time)))

        duration = i["Duration"]
        duration = duration.replace(" days", "d")
        duration = duration.replace(" day", "d")
        tr.append(TD(duration))
        tr.append(TD(A(I(_class="fa fa-external-link-square fa-lg"),
                       _class="btn-floating btn-small green accent-4 tooltipped",
                       _href=i["url"],
                       data={"position": "left",
                             "tooltip": "Contest Link",
                             "delay": "50"},
                       _target="_blank")))
        tr.append(TD(BUTTON(I(_class="fa fa-calendar-plus-o"),
                            _class="btn-floating btn-small orange accent-4 tooltipped",
                            data={"position": "left",
                                  "tooltip": "Set Reminder to Google Calendar",
                                  "delay": "50"},
                            _id="set-reminder-" + str(button_id))))
        tbody.append(tr)
        button_id += 1

    table.append(tbody)
    return dict(table=table, upcoming=upcoming)

# ------------------------------------------------------------------------------
def send_reminder():
    return dict()

# ------------------------------------------------------------------------------
def leaderboard():
    """
        Get a table with users sorted by rating
    """

    specific_institute = False
    atable = db.auth_user
    cftable = db.custom_friend

    afields = ["first_name", "last_name", "stopstalk_handle",
               "institute", "per_day", "rating"]
    cfields = afields + ["duplicate_cu"]
    if request.vars.has_key("q"):
        institute = request.vars["q"]
        if institute != "":
            specific_institute = True
            reg_users = db(atable.institute == institute).select(*afields)
            custom_users = db(cftable.institute == institute).select(*cfields)

    if specific_institute is False:
        reg_users = db(atable).select(*afields)
        custom_users = db(cftable).select(*cfields)

    # Find the total solved problems(Lesser than total accepted)
    solved_count = {}
    sql = """
             SELECT stopstalk_handle, COUNT(DISTINCT(problem_name))
             FROM submission
             WHERE status = 'AC'
             GROUP BY user_id, custom_user_id;
          """
    tmplist = db.executesql(sql)
    for user in tmplist:
        solved_count[user[0]] = user[1]

    users = []
    for user in reg_users:
        try:
            solved = solved_count[user.stopstalk_handle]
        except KeyError:
            solved = 0

        tup = utilities.compute_row(user, solved)
        if tup is not ():
            users.append(tup)

    for user in custom_users:
        try:
            if user.duplicate_cu:
                orig_user = cftable(user.duplicate_cu)
                solved = solved_count[orig_user.stopstalk_handle]
            else:
                solved = solved_count[user.stopstalk_handle]
        except KeyError:
            solved = 0
        tup = utilities.compute_row(user, solved, True)
        if tup is not ():
            users.append(tup)

    # Sort users according to the rating
    users = sorted(users, key=lambda x: x[3], reverse=True)

    table = TABLE(_class="centered striped")
    table.append(THEAD(TR(TH("Rank"),
                          TH("Name"),
                          TH("StopStalk Handle"),
                          TH("Institute"),
                          TH("StopStalk Rating"),
                          TH("Rating Changes"),
                          TH("Per Day Changes"))))

    tbody = TBODY()
    rank = 1
    for i in users:

        if i[5]:
            span = SPAN(_class="orange tooltipped",
                        data={"position": "right",
                              "delay": "50",
                              "tooltip": "Custom User"},
                        _style="cursor: pointer; " + \
                                "float:right; " + \
                                "height:10px; " + \
                                "width:10px; " + \
                                "border-radius: 50%;")
        else:
            span = SPAN()

        tr = TR()
        tr.append(TD(str(rank) + "."))
        tr.append(TD(DIV(span, DIV(i[0]))))
        tr.append(TD(A(i[1],
                       _href=URL("user", "profile", args=[i[1]]),
                       _target="_blank")))
        tr.append(TD(A(i[2],
                       _href=URL("default", "leaderboard", vars={"q": i[2]}))))
        tr.append(TD(i[3]))
        if i[6] > 0:
            tr.append(TD(B("+%s" % str(i[6])), _class="green-text text-darken-2"))
        elif i[6] < 0:
            tr.append(TD(B(i[6]), _class="red-text text-darken-2"))
        else:
            tr.append(TD(i[6], _class="blue-text text-darken-2"))

        diff = "{:1.5f}".format(i[4])

        if float(diff) == 0.0:
            tr.append(TD("+" + diff, " ",
                         I(_class="fa fa-minus")))
        elif i[4] > 0:
            tr.append(TD("+" + str(diff), " ",
                         I(_class="fa fa-chevron-circle-up",
                           _style="color: #0f0;")))
        elif i[4] < 0:
            tr.append(TD(diff, " ",
                         I(_class="fa fa-chevron-circle-down",
                           _style="color: #f00;")))

        tbody.append(tr)
        rank += 1

    table.append(tbody)
    return dict(table=table)

# ----------------------------------------------------------------------------
def user():
    """
        Use the standard auth for user
    """
    return dict(form=auth())

# ----------------------------------------------------------------------------
@auth.requires_login()
def search():
    """
        Search for a user
    """

    return dict()

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
        page -= 1

    all_languages = db(stable).select(stable.lang,
                                      distinct=True)
    languages = []
    for  i in all_languages:
        languages.append(i["lang"])

    table = None
    # If form is not submitted
    if get_vars == {}:
        return dict(languages=languages,
                    table=table)

    # Form has been submitted
    cftable = db.custom_friend
    atable = db.auth_user
    ftable = db.friends
    duplicates = []

    if session.auth:

        # Retrieve all the custom users created by the logged-in user
        query = (cftable.first_name.contains(get_vars["name"]))
        query |= (cftable.last_name.contains(get_vars["name"]))
        query &= (cftable.user_id == session.user_id)
        cust_friends = db(query).select(cftable.id, cftable.duplicate_cu)

        # The Original IDs of duplicate custom_friends
        custom_friends = []
        for cus_id in cust_friends:
            if cus_id.duplicate_cu:
                duplicates.append((cus_id.id, cus_id.duplicate_cu))
                custom_friends.append(cus_id.duplicate_cu)
            else:
                custom_friends.append(cus_id.id)

        # Get the friends of logged in user
        query = (atable.first_name.contains(get_vars["name"]))
        query |= (atable.last_name.contains(get_vars["name"]))

        # @ToDo: Anyway to use join instead of two such db calls
        possible_users = db(query).select(atable.id)
        possible_users = [x["id"] for x in possible_users]

        query = (ftable.user_id == session.user_id)
        query &= (ftable.friend_id.belongs(possible_users))
        friend_ids = db(query).select(ftable.friend_id)
        friends = [x["friend_id"] for x in friend_ids]

        if session.user_id in possible_users:
            # Show submissions of user also
            friends.append(session.user_id)

        # User in one of the friends
        query = (stable.user_id.belongs(friends))

        # User in one of the custom friends
        query |= (stable.custom_user_id.belongs(custom_friends))
    else:
        # Retrieve all the custom users
        query = (cftable.first_name.contains(get_vars["name"]))
        query |= (cftable.last_name.contains(get_vars["name"]))
        custom_friends = db(query).select(cftable.id)
        cusfriends = [x["id"] for x in custom_friends]

        # Get the users registered
        query = (atable.first_name.contains(get_vars["name"]))
        query |= (atable.last_name.contains(get_vars["name"]))
        user_ids = db(query).select(atable.id)
        registered_users = [x["id"] for x in user_ids]

        # User in one of the friends
        query = (stable.user_id.belongs(registered_users))

        # User in one of the custom friends
        query |= (stable.custom_user_id.belongs(cusfriends))

    start_date = get_vars["start_date"]
    end_date = get_vars["end_date"]

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

    start_time = time.strptime(start_date, "%Y-%m-%d %H:%M:%S")
    end_time = time.strptime(end_date, "%Y-%m-%d %H:%M:%S")

    if end_time > start_time:
        # Submissions in the the range start_date to end_date
        query &= (stable.time_stamp >= start_date)
        query &= (stable.time_stamp <= end_date)
    else:
        session.flash = "Start Date greater than End Date"
        redirect(URL("default", "filters"))

    # Submissions with problem name containing pname
    if get_vars["pname"] != "":
        query &= (stable.problem_name.contains(get_vars["pname"]))

    # Submissions from this site
    if get_vars.has_key("site"):
        sites = get_vars["site"]
        if isinstance(sites, str):
            sites = [sites]
        query &= (stable.site.belongs(sites))

    # Submissions with this language
    if get_vars.has_key("language"):
        langs = get_vars["language"]
        if isinstance(langs, str):
            langs = [langs]
        query &= (stable.lang.belongs(langs))

    # Submissions with this submission status
    if get_vars.has_key("status"):
        statuses = get_vars["status"]
        if isinstance(statuses, str):
            statuses = [statuses]
        query &= (stable.status.belongs(statuses))

    PER_PAGE = current.PER_PAGE
    # Apply the complex query and sort by time_stamp DESC
    filtered = db(query).select(limitby=(page * PER_PAGE,
                                         (page + 1) * PER_PAGE),
                                orderby=~stable.time_stamp)

    total_problems = db(query).count()
    total_pages = total_problems / 100
    if total_problems % 100 == 0:
        total_pages += 1

    table = utilities.render_table(filtered, duplicates)

    return dict(languages=languages,
                table=table,
                total_pages=total_pages)

# ----------------------------------------------------------------------------
@auth.requires_login()
def mark_friend():
    """
        Send a friend request
    """

    if len(request.args) < 1:
        session.flash = "Invalid URL"
        redirect(URL("default", "search"))

    frtable = db.friend_requests
    ftable = db.friends
    friend_id = long(request.args[0])

    if friend_id != session.user_id:
        query = (ftable.user_id == session.user_id)
        query &= (ftable.friend_id == friend_id)
        value = db(query).count()
        if value == 0:
            query = (frtable.from_h == session.user_id)
            query &= (frtable.to_h == friend_id)
            query |= (frtable.from_h == friend_id) & \
                     (frtable.to_h == session.user_id)

            value = db(query).count()
            if value != 0:
                session.flash = "Friend request pending..."
                redirect(URL("default", "search"))
        else:
            session.flash = "Already friends !!"
            redirect(URL("default", "search"))
    else:
        session.flash = "Invalid user argument!"
        redirect(URL("default", "search"))

    # Insert a tuple of users' id into the friend_requests table
    db.friend_requests.insert(from_h=session.user_id, to_h=friend_id)

    # Send the user an email notifying about the request
    atable = db.auth_user
    query = (atable.id == friend_id)
    row = db(query).select(atable.email,
                           atable.stopstalk_handle).first()
    current.send_mail(to=row.email,
                      subject=session.handle + \
                              " wants to be a friend on StopStalk",
                      message=session.handle + \
                              "(" + (URL("user",
                                         "profile",
                                         args=[session.handle],
                                         scheme=True,
                                         host=True,
                                         extension=False)) + \
                      ") wants to connect on StopStalk\n\n" + \
                      "To view all friend requests go here - " + \
                      URL("user",
                          "friend_requests",
                          scheme=True,
                          host=True,
                          extension=False))

    session.flash = "Friend Request sent"
    redirect(URL("default", "search.html"))
    return dict()

# ----------------------------------------------------------------------------
@auth.requires_login()
def retrieve_users():
    """
        Show the list of registered users
    """

    atable = db.auth_user
    frtable = db.friend_requests
    ftable = db.friends
    q = request.get_vars.get("q", None)

    query = (atable.first_name.contains(q))
    query |= (atable.last_name.contains(q))
    query |= (atable.stopstalk_handle.contains(q))

    for site in current.SITES:
        field_name = site.lower() + "_handle"
        query |= (atable[field_name].contains(q))

    # Don't show the logged in user in the search
    query &= (atable.id != session.user_id)

    # Don't show users who have sent friend requests
    # to the logged in user
    tmprows = db(frtable.to_h == session.user_id).select(frtable.from_h)
    for row in tmprows:
        query &= (atable.id != row.from_h)

    # Columns of auth_user to be retrieved
    columns = [atable.id,
               atable.first_name,
               atable.last_name,
               atable.stopstalk_handle]

    for site in current.SITES:
        columns.append(atable[site.lower() + "_handle"])

    rows = db(query).select(*columns)

    t = TABLE(_class="striped centered")
    tr = TR(TH("Name"),
            TH("StopStalk Handle"))

    for site in current.SITES:
        tr.append(TH(site + " Handle"))

    tr.append(TH("Friendship Status"))
    thead = THEAD()
    thead.append(tr)
    t.append(thead)

    tbody = TBODY()

    query = (ftable.user_id == session["user_id"])
    friends = db(query).select(atable.id,
                               join=ftable.on(ftable.friend_id == atable.id))
    friends = [x["id"] for x in friends]

    for user in rows:

        tr = TR()
        tr.append(TD(A(user.first_name + " " + user.last_name,
                       _href=URL("user", "profile",
                                 args=[user.stopstalk_handle],
                                 extension=False),
                       _target="_blank")))
        tr.append(TD(user.stopstalk_handle))

        for site in current.SITES:
            tr.append(TD(user[site.lower() + "_handle"]))

        # Check if the current user is already a friend or not
        if user.id not in friends:
            r = db((frtable.from_h == session.user_id) &
                   (frtable.to_h == user.id)).count()
            if r == 0:
                tr.append(TD(A(I(_class="fa fa-user-plus fa-3x"),
                               _class="tooltipped btn-floating btn-large waves-effect waves-light green",
                               data={"position": "bottom",
                                     "delay": "50",
                                     "tooltip": "Send friend request"},
                               _href=URL("default", "mark_friend",
                                         args=[user.id]))))
            else:
                tr.append(TD(BUTTON(I(_class="fa fa-user-plus fa-3x"),
                                    _class="tooltipped btn-floating btn-large disabled",
                                    data={"position": "bottom",
                                          "delay": "50",
                                          "tooltip": "Send friend request"})))
        else:
            tr.append(TD(A(I(_class="fa fa-user-times fa-3x"),
                           _class="tooltipped btn-floating btn-large waves-effect waves-light black",
                           data={"position": "bottom",
                                 "delay": "50",
                                 "tooltip": "Friend request sent"},
                           _href=URL("default", "unfriend", args=[user.id]))))
        tbody.append(tr)

    t.append(tbody)
    return dict(t=t)

# ----------------------------------------------------------------------------
@auth.requires_login()
def unfriend():
    """
        Unfriend the user
    """

    if len(request.args) != 1:
        session.flash = "Please click on a button!"
        redirect(URL("default", "search"))
    else:
        friend_id = long(request.args[0])
        user_id = session["user_id"]
        ftable = db.friends

        # Delete records in the friends table
        query = (ftable.user_id == user_id) & (ftable.friend_id == friend_id)
        value = db(query).count()
        if value == 0:
            session.flash = "Invalid URL"
            redirect(URL("default", "search"))
        db(query).delete()
        query = (ftable.user_id == friend_id) & (ftable.friend_id == user_id)
        db(query).delete()

        # Send email to the friend notifying about the tragedy ;)
        atable = db.auth_user
        row = db(atable.id == friend_id).select(atable.email).first()
        current.send_mail(to=row.email,
                          subject="A friend unfriended you on StopStalk",
                          message=session.handle + \
                                  "(" + (URL("user",
                                             "profile",
                                             args=[session.handle],
                                             scheme=True,
                                             host=True,
                                             extension=False)) + \
                          ") unfriended you on StopStalk")

        session.flash = "Successfully unfriended"
        redirect(URL("default", "search.html"))

# ----------------------------------------------------------------------------
@auth.requires_login()
def submissions():
    """
        Retrieve submissions of the logged-in user
    """

    if len(request.args) == 0:
        active = "1"
    else:
        active = request.args[0]

    cftable = db.custom_friend
    ftable = db.friends
    stable = db.submission
    atable = db.auth_user

    # Get all the friends/custom friends of the logged-in user
    friends, cusfriends = utilities.get_friends(session["user_id"])

    # The Original IDs of duplicate custom_friends
    custom_friends = []
    for cus_id in cusfriends:
        if cus_id[1] == None:
            custom_friends.append(cus_id[0])
        else:
            custom_friends.append(cus_id[1])

    query = (stable.user_id.belongs(friends))
    query |= (stable.custom_user_id.belongs(custom_friends))
    total_count = db(query).count()

    PER_PAGE = current.PER_PAGE
    count = total_count / PER_PAGE
    if total_count % PER_PAGE:
        count += 1

    if request.extension == "json":
        return dict(count=count,
                    total_rows=1)

    offset = PER_PAGE * (int(active) - 1)
    # Retrieve only some number of submissions from the offset
    rows = db(query).select(orderby=~db.submission.time_stamp,
                            limitby=(offset, offset + PER_PAGE))

    table = utilities.render_table(rows, cusfriends)
    return dict(table=table,
                friends=friends,
                cusfriends=cusfriends,
                total_rows=len(rows))

# ----------------------------------------------------------------------------
def faq():
    """
        FAQ page
    """

    div = DIV(_class="row")
    ul = UL(_class="collapsible col offset-s3 s6", data={"collapsible": "expandable"})

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
    if session["auth"]:
        user = session["auth"]["user"]
        ctable.email.default = user["email"]
        ctable.name.default = user["first_name"] + " " + user["last_name"]

    form = SQLFORM(ctable)

    if form.process(keepvalues=True).accepted:
        session.flash = "We will get back to you!"
        current.send_mail(to="contactstopstalk@gmail.com",
                          subject="We got feedback!",
                          message="From: %s (%s - %s)\n" % \
                                    (form.vars.name,
                                     form.vars.email,
                                     form.vars.phone_number) + \
                                  "Subject: %s\n" % form.vars.subject + \
                                  "Message: %s\n" % form.vars.text_message)
        redirect(URL("default", "index"))
    elif form.errors:
        response.flash = "Form has errors!"

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

# END =========================================================================
