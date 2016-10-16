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
import utilities

# ----------------------------------------------------------------------------
def handle_error():
    """
        Handles errors and shows valid error messages
        Also notifies the admin by an email
    """

    def _get_similar_handles(url):

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
                                  atable.stopstalk_handle)
        custom_users = db(cftable).select(cftable.first_name,
                                          cftable.last_name,
                                          cftable.stopstalk_handle)

        prospects.extend([(x.first_name,
                           x.last_name,
                           x.stopstalk_handle) for x in users])
        prospects.extend([(x.first_name,
                           x.last_name,
                           x.stopstalk_handle) for x in custom_users])

        similar_handles = []
        for prospect in prospects:
            fname, lname, stopstalk_handle = prospect
            diff1 = SequenceMatcher(None, fname.lower(), handle).ratio()
            diff2 = SequenceMatcher(None, lname.lower(), handle).ratio()
            diff3 = SequenceMatcher(None, stopstalk_handle.lower(), handle).ratio()
            diff = max(diff1, diff2, diff3)
            if diff >= 0.8:
                similar_handles.append((stopstalk_handle, diff))

        similar_handles.sort(key=lambda x: x[1], reverse=True)

        return [x[0] for x in similar_handles]

    code = request.vars.code
    request_url = request.vars.request_url
    ticket = request.vars.ticket

    # Make sure error url is not current url to avoid infinite loop.
    if code is not None and request_url != request.url:
        # Assign the error status code to the current response
        response.status = int(code)

    error_message = ""
    similar_handles = []
    if code == "404":
        similar_handles = _get_similar_handles(request_url)
        message = request_url + " " + str(similar_handles)
        error_message = "Not found"
    elif code == "500":
        # Get ticket URL:
        message = URL("admin", "default", "ticket",
                      args=ticket,
                      scheme=True,
                      host=True)
        error_message = "Internal Server error"
    else:
        message = request_url
        error_message = "Other error"

    if auth.is_logged_in():
        subject = "%s %s occurred" % (session.auth.user.email, code)
    else:
        subject = "%s occurred" % code

    current.send_mail(to="raj454raj@gmail.com",
                      subject=subject,
                      message=message,
                      mail_type="admin",
                      bulk=True)

    return dict(error_message=error_message, similar_handles=similar_handles)

# ----------------------------------------------------------------------------
def index():
    """
        The main controller which redirects depending
        on the login status of the user and does some
        extra pre-processing
    """
    # If the user is logged in
    if auth.is_logged_in():
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

    if not auth.is_logged_in():
        redirect(URL("default", "index"))

    ftable = db.friends
    atable = db.auth_user
    cftable = db.custom_friend

    # Check for streak of friends on stopstalk
    query = (ftable.user_id == session.user_id)
    rows = db(query).select(atable.first_name,
                            atable.last_name,
                            atable.stopstalk_handle,
                            join=ftable.on(ftable.friend_id == atable.id))

    # Will contain list of handles of all the friends along
    # with the Custom Users added by the logged-in user
    handles = []

    complete_dict = {}
    friends_stopstalk_handles = []
    for user in rows:
        complete_dict[user.stopstalk_handle] = []
        friends_stopstalk_handles.append("'" + user.stopstalk_handle + "'")
        handles.append((user.stopstalk_handle,
                        user.first_name + " " + user.last_name,
                        user.stopstalk_handle))

    # Check for streak of custom friends
    query = (cftable.user_id == session.user_id)
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
        complete_dict[stopstalk_handle] = []
        friends_stopstalk_handles.append("'" + stopstalk_handle + "'")

    if friends_stopstalk_handles == []:
        friends_stopstalk_handles = ["-1"]

    # Build the complex SQL query
    sql_query = """
                    SELECT stopstalk_handle, DATE(time_stamp), COUNT(*) as cnt
                    FROM submission
                    WHERE stopstalk_handle in (%s)
                    GROUP BY stopstalk_handle, DATE(submission.time_stamp)
                    ORDER BY time_stamp;
                """ % (", ".join(friends_stopstalk_handles))

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
    table = TABLE(THEAD(TR(TH(STRONG("User")),
                           TH(STRONG("Days")))),
                  _class="col offset-s3 s6 striped centered")

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

    table.append(tbody)
    if len(users_on_day_streak) == 0:
        table = H6("No friends on day streak", _class="center")

    return dict(table=table)

# ----------------------------------------------------------------------------
@auth.requires_login()
def unsubscribe():

    utable = db.unsubscriber
    utable.email.default = session.auth.user.email
    utable.email.writable = False

    form = SQLFORM(utable,
                   submit_button="Update Subscription")

    record = db(utable.email == session.auth.user.email).select().first()
    if record:
        form = SQLFORM(utable,
                       record,
                       showid=False,
                       submit_button="Update Subscription")

    if form.process().accepted:
        response.flash = "Subscription details updated"
        redirect(URL("default", "unsubscribe"))
    elif form.errors:
        response.flash = "Form has errors"

    return dict(form=form)

# ----------------------------------------------------------------------------
@auth.requires_login()
def my_friends():
    """
        Display the friends data
    """

    ftable = db.friends

    rows = db(ftable.user_id == session.user_id).select(ftable.friend_id)
    table = TABLE(THEAD(TR(TH("Friend name"),
                           TH("Authentic user"),
                           TH("Institute friend"),
                           TH("Other friend"),
                           TH("Claimable"))),
                  _class="centered col offset-s3 s6")

    tbody = TBODY()
    check = I(_class="fa fa-check",
              _style="color: #0f0")
    cross = I(_class="fa fa-close",
              _style="color: #f00")

    valid_friends = 0
    for row in rows:
        claimable = True
        thisfriend = row.friend_id
        name = thisfriend.first_name + " " + thisfriend.last_name
        tr = TR(TD(A(name, _href=URL("user", "profile",
                                     args=thisfriend.stopstalk_handle))))
        claimable &= thisfriend.authentic
        if thisfriend.authentic:
            tr.append(check)
        else:
            tr.append(cross)

        query = (ftable.user_id == thisfriend)
        friends_of_friends = db(query).select(ftable.friend_id)
        institute_friends = 0
        for fof in friends_of_friends:
            if fof.friend_id.institute == thisfriend.institute and \
               fof.friend_id.institute != "Other":
                institute_friends += 1
        if institute_friends > 1:
            tr.append(TD(check))
            tr.append(TD(check))
        else:
            if institute_friends == 0:
                claimable &= False
                tr.append(cross)
                if len(friends_of_friends) >= 2:
                    tr.append(check)
                else:
                    tr.append(cross)
            else:
                tr.append(check)
                if len(friends_of_friends) >= 3:
                    claimable &= True
                    tr.append(check)
                else:
                    claimable &= False
                    tr.append(cross)


        if claimable:
            valid_friends += 1
            tr.append(TD(I(_class="fa fa-thumbs-up")))
        else:
            tr.append(TD())
        tbody.append(tr)

    table.append(tbody)

    claimable_stickers = valid_friends/3
    stickers = [claimable_stickers/3] * 3
    residue = claimable_stickers - (claimable_stickers/3) * 3
    i = 0
    while residue:
        stickers[i] += 1
        i += 1
        residue -= 1

    return dict(table=DIV(table, _class="row"),
                claimable_stickers=claimable_stickers,
                stickers=stickers)

# ----------------------------------------------------------------------------
def log_contest():
    """
        Logging contests into DB
    """

    pvars = request.post_vars

    if pvars.contest_name is None or \
       pvars.site_name is None or \
       pvars.contest_link is None or \
       pvars.logging_type is None:
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

    table = TABLE(_class="centered striped", _id="contests-table")
    thead = THEAD(TR(TH("Contest Name"),
                     TH("Site"),
                     TH("Start"),
                     TH("Duration/Ending"),
                     TH("Link"),
                     TH("Add Reminder")))
    table.append(thead)
    tbody = TBODY()

    button_class = "btn-floating btn-small accent-4 tooltipped"
    view_link_class = button_class + " green view-contest"
    reminder_class = button_class + " orange set-reminder"

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
        tr.append(TD(str(endtime).replace("-", "/"),
                     _class="contest-end-time"))
        tr.append(TD(A(I(_class="fa fa-external-link-square fa-lg"),
                       _class=view_link_class,
                       _href=i["url"],
                       data={"position": "left",
                             "tooltip": "Contest Link",
                             "delay": "50"},
                       _target="_blank")))
        tr.append(TD(BUTTON(I(_class="fa fa-calendar-plus-o"),
                            _class=reminder_class + " disabled",
                            data={"position": "left",
                                  "tooltip": "Already started!",
                                  "delay": "50"})))
        tbody.append(tr)

    for i in upcoming:

        if i["Platform"] in ("TOPCODER", "OTHER"):
            continue

        start_time = datetime.datetime.strptime(i["StartTime"],
                                                "%a, %d %b %Y %H:%M")
        tr = TR()
        tr.append(TD(i["Name"]))
        tr.append(TD(i["Platform"].capitalize()))
        tr.append(TD(str(start_time), _class="stopstalk-timestamp"))

        duration = i["Duration"]
        duration = duration.replace(" days", "d")
        duration = duration.replace(" day", "d")
        tr.append(TD(duration))
        tr.append(TD(A(I(_class="fa fa-external-link-square fa-lg"),
                       _class=view_link_class,
                       _href=i["url"],
                       data={"position": "left",
                             "tooltip": "Contest Link",
                             "delay": "50"},
                       _target="_blank")))
        tr.append(TD(BUTTON(I(_class="fa fa-calendar-plus-o"),
                            _class=reminder_class,
                            data={"position": "left",
                                  "tooltip": "Set Reminder to Google Calendar",
                                  "delay": "50"})))
        tbody.append(tr)

    table.append(tbody)
    return dict(table=table, upcoming=upcoming, retrieved=True)

# ------------------------------------------------------------------------------
def leaderboard():
    """
        Get a table with users sorted by rating
    """

    specific_institute = False
    atable = db.auth_user
    cftable = db.custom_friend

    global_leaderboard = False
    if request.vars.has_key("global"):
        if request.vars["global"] == "True":
            global_leaderboard = True
        else:
            if not auth.is_logged_in():
                response.flash = "Login to see Friends Leaderboard"
                global_leaderboard = True
    else:
        if not auth.is_logged_in():
            global_leaderboard = True

    heading = "Global Leaderboard"
    afields = ["first_name", "last_name", "stopstalk_handle", "rating",
               "institute", "per_day", "prev_rating", "per_day_change"]
    cfields = afields + ["duplicate_cu"]

    aquery = (atable.id > 0)
    cquery = (cftable.id > 0)
    if global_leaderboard is False:
        if auth.is_logged_in():
            heading = "Friends Leaderboard"
            friends, cusfriends = utilities.get_friends(session.user_id)
            custom_friends = [x[0] for x in cusfriends]

            # Add logged-in user to leaderboard
            friends.append(session.user_id)
            aquery &= (atable.id.belongs(friends))
            cquery &= (cftable.id.belongs(custom_friends))
        else:
            aquery &= (1 == 0)
            cquery &= (1 == 0)

    # Do not display unverified users in the leaderboard
    aquery &= (atable.registration_key == "")

    if request.vars.has_key("q"):
        heading = "Institute Leaderboard"
        institute = request.vars["q"]

        if institute != "":
            specific_institute = True
            aquery &= (atable.institute == institute)
            cquery &= (cftable.institute == institute)
            reg_users = db(aquery).select(*afields)
            custom_users = db(cquery).select(*cfields)

    if specific_institute is False:
        reg_users = db(aquery).select(*afields)
        custom_users = db(cquery).select(*cfields)

    users = []
    for user in reg_users:
        users.append((user.first_name + " " + user.last_name,
                      user.stopstalk_handle,
                      user.institute,
                      int(user.rating),
                      float(user.per_day_change),
                      False,
                      int(user.rating) - int(user.prev_rating)))

    for user in custom_users:
        if user.duplicate_cu:
            record = cftable(user.duplicate_cu)
        else:
            record = user
        users.append((user.first_name + " " + user.last_name,
                      user.stopstalk_handle,
                      user.institute,
                      int(record.rating),
                      float(record.per_day_change),
                      True,
                      int(record.rating) - int(record.prev_rating)))

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
                       _href=URL("default",
                                 "leaderboard",
                                 vars={"q": i[2],
                                       "global": global_leaderboard}))))
        tr.append(TD(i[3]))
        if i[6] > 0:
            tr.append(TD(B("+%s" % str(i[6])),
                         _class="green-text text-darken-2"))
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
    switch = DIV(LABEL(H6("Friends' Submissions",
                          INPUT(_type="checkbox", _id="submission-switch"),
                          SPAN(_class="lever pink accent-3"),
                          "Global Submissions")),
                 _class="switch")
    div = TAG[""](switch, table)
    return dict(div=div,
                heading=heading,
                global_leaderboard=global_leaderboard)

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
        page -= 1

    all_languages = db(stable).select(stable.lang,
                                      distinct=True)
    languages = [x["lang"] for x in all_languages]

    table = None
    global_submissions = False
    if get_vars.has_key("global"):
        if get_vars["global"] == "True":
            global_submissions = True

    # If form is not submitted
    if get_vars == {}:
        return dict(languages=languages,
                    div=DIV(),
                    global_submissions=global_submissions)

    # If nothing is filled in the form
    # these fields should be passed in
    # the URL with empty value
    compulsary_keys = ["pname", "name", "end_date", "start_date"]
    if set(compulsary_keys).issubset(get_vars.keys()) is False:
        session.flash = "Invalid URL parameters"
        redirect(URL("default", "filters"))

    # Form has been submitted
    cftable = db.custom_friend
    atable = db.auth_user
    ftable = db.friends
    duplicates = []

    switch = DIV(LABEL(H6("Friends' Submissions",
                          INPUT(_type="checkbox", _id="submission-switch"),
                          SPAN(_class="lever pink accent-3"),
                          "Global Submissions")),
                 _class="switch")
    table = TABLE()
    div = TAG[""](H4("Recent Submissions"), switch, table)

    if global_submissions is False and not auth.is_logged_in():
        session.flash = "Login to view Friends' submissions"
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

    query = True
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
    possible_users = [x["id"] for x in possible_users]
    friends = possible_users

    if global_submissions is False:
        query = (ftable.user_id == session.user_id) & \
                (ftable.friend_id.belongs(possible_users))
        friend_ids = db(query).select(ftable.friend_id)
        friends = [x["friend_id"] for x in friend_ids]

        if session.user_id in possible_users:
            # Show submissions of user also
            friends.append(session.user_id)

    # User in one of the friends
    query = (stable.user_id.belongs(friends))

    # User in one of the custom friends
    query |= (stable.custom_user_id.belongs(custom_friends))

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
        query &= (stable.time_stamp >= start_date) & \
                 (stable.time_stamp <= end_date)
    else:
        session.flash = "Start Date greater than End Date"
        redirect(URL("default", "filters"))

    pname = get_vars["pname"]
    # Submissions with problem name containing pname
    if pname != "":
        pname = pname.split()
        for token in pname:
            query &= (stable.problem_name.contains(token))

    # Check if multiple parameters are passed
    def _get_values_list(param_name):

        values_list = None
        if get_vars.has_key(param_name):
            values_list = get_vars[param_name]
            if isinstance(values_list, str):
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
    filtered = db(query).select(limitby=(page * PER_PAGE,
                                         (page + 1) * PER_PAGE),
                                orderby=~stable.time_stamp)

    total_problems = db(query).count()
    total_pages = total_problems / 100
    if total_problems % 100 == 0:
        total_pages += 1

    table = utilities.render_table(filtered, duplicates)
    switch = DIV(LABEL(H6("Friends' Submissions",
                          INPUT(_type="checkbox", _id="submission-switch"),
                          SPAN(_class="lever pink accent-3"),
                          "Global Submissions")),
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
        Send a friend request
    """

    if len(request.args) < 1:
        return "Invalid URL"

    frtable = db.friend_requests
    ftable = db.friends
    friend_id = long(request.args[0])

    if friend_id != session.user_id:
        query = (ftable.user_id == session.user_id) & \
                (ftable.friend_id == friend_id)
        value = db(query).count()
        if value == 0:
            query = ((frtable.from_h == session.user_id) & \
                     (frtable.to_h == friend_id)) | \
                    ((frtable.from_h == friend_id) & \
                     (frtable.to_h == session.user_id))

            value = db(query).count()
            if value != 0:
                session.flash = "Friend request pending..."
                redirect(URL("default", "search"))
        else:
            return "Already friends !!"
    else:
        return "Invalid user argument!"

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
                      message="""<html>
%s (%s) wants to connect on StopStalk <br />
To view all friend requests go here - %s <br />

To stop receiving mails - <a href="%s">Unsubscribe</a></html>
                              """ % (session.handle,
                                     URL("user",
                                         "profile",
                                         args=[session.handle],
                                         scheme=True,
                                         host=True,
                                         extension=False),
                                     URL("user",
                                         "friend_requests",
                                         scheme=True,
                                         host=True,
                                         extension=False),
                                     URL("default", "unsubscribe",
                                         scheme=True,
                                         host=True,
                                         extension=False)),
                      mail_type="friend_requests")

    return "Friend Request sent"

# ----------------------------------------------------------------------------
def search():
    """
        Show the list of registered users
    """

    # Get all the list of institutes for the dropdown
    itable = db.institutes
    all_institutes = db(itable).select(itable.name,
                                       orderby=itable.name)
    all_institutes = [x["name"].strip("\"") for x in all_institutes]
    all_institutes.append("Other")

    # Return if form is not submitted
    if len(request.get_vars) == 0:
        return dict(all_institutes=all_institutes,
                    table=DIV())

    atable = db.auth_user
    frtable = db.friend_requests
    ftable = db.friends
    q = request.get_vars.get("q", None)
    institute = request.get_vars.get("institute", None)

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
        # Don't show users who have sent friend requests
        # to the logged in user
        tmprows = db(frtable.to_h == session.user_id).select(frtable.from_h)
        for row in tmprows:
            query &= (atable.id != row.from_h)

    # Search by institute (if provided)
    if institute:
        query &= (atable.institute == institute)

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

    table = TABLE(_class="striped centered")
    tr = TR(TH("Name"))

    for site in current.SITES:
        tr.append(TH(site + " Handle"))

    if auth.is_logged_in():
        tr.append(TH("Friendship Status"))

    thead = THEAD()
    thead.append(tr)
    table.append(thead)

    tbody = TBODY()

    if auth.is_logged_in():
        query = (ftable.user_id == session.user_id)
        join_query = (ftable.friend_id == atable.id)
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
                       _target="_blank")))

        for site in current.SITES:
            tr.append(TD(user[site.lower() + "_handle"]))

        # If user is not logged in then no need to show the
        # friend request buttons
        if auth.is_logged_in() is False:
            tbody.append(tr)
            continue

        # Tooltip data attributes
        tooltip_attrs = [None, None, str(user.id)]

        # Check if the current user is already a friend or not
        if user.id not in friends:
            r = db((frtable.from_h == session.user_id) &
                   (frtable.to_h == user.id)).count()
            if r == 0:
                # Not a friend and no friend request pending
                tooltip_attrs[:2] = "Send friend request", "add-friend"
                tr.append(TD(BUTTON(I(_class="fa fa-user-plus fa-3x"),
                                    _class=btn_class + " green",
                                    data=_get_tooltip_data(*tooltip_attrs))))
            else:
                # Not a friend and friend request pending
                tooltip_attrs[:2] = "Friend request pending", "disabled"
                tr.append(TD(BUTTON(I(_class="fa fa-user-plus fa-3x"),
                                    _class=btn_class + " disabled",
                                    data=_get_tooltip_data(*tooltip_attrs))))
        else:
            # Already friends
            tooltip_attrs[:2] = "Unfriend", "unfriend"
            tr.append(TD(BUTTON(I(_class="fa fa-user-times fa-3x"),
                                _class=btn_class + " black",
                                data=_get_tooltip_data(*tooltip_attrs))))
        tbody.append(tr)

    table.append(tbody)
    return dict(all_institutes=all_institutes, table=table)

# ----------------------------------------------------------------------------
@auth.requires_login()
def download_submission():
    """
        Return the downloaded submission as a string
    """

    from bs4 import BeautifulSoup

    def _handle_retrieve_error(download_url,
                               status_code,
                               error=None,
                               message_body=None):

        """
            Error logging for Download submissions

            @param download_url (String): Download URL which failed
            @param status_code (Number): Status code of response
            @param error (String): Exception message
            @param message_body (String): response.text in case of errors

            @return Number: -1 (To signify failure to JS)
        """

        subject = "Download submission failed: %d" % status_code
        message = """
User handle: %s
Download URL: %s
Error: %s
Response text: %s
                  """ % (session.handle, download_url, error, message_body)

        current.send_mail(to="raj454raj@gmail.com",
                          subject=subject,
                          message=message,
                          mail_type="admin",
                          bulk=True)
        return -1

    def _response_handler(download_url, response):
        """
            Handle the request response

            @param response (Response): Response object after request to the
                                        view submission link
            @return Number (-1) / String (Submission code)
        """

        if response.status_code != 200:
            return _handle_retrieve_error(download_url,
                                          response.status_code)

        try:
            return BeautifulSoup(response.text, "lxml").find("pre").text
        except Exception as e:
            return _handle_retrieve_error(download_url,
                                          response.status_code,
                                          e,
                                          response.text)

    def _retrieve_codechef_submission(view_link):
        """
            Get CodeChef submission from view_link

            @param view_link (String): View link of the submission
            @return _response_handler (Method): Handler for the response
        """

        problem_id = view_link.strip("/").split("/")[-1]
        download_url = "https://www.codechef.com/viewplaintext/" + \
                       str(problem_id)
        response = requests.get(download_url)
        return _response_handler(download_url, response)

    def _retrieve_codeforces_submission(view_link):
        """
            Get Codeforces submission from view_link

            @param view_link (String): View link of the submission
            @return _response_handler (Method): Handler for the response
        """

        response = requests.get(view_link)
        return _response_handler(view_link, response)

    site = request.get_vars["site"]
    view_link = request.get_vars["viewLink"]
    db.download_submission_logs.insert(user_id=session.user_id,
                                       url=view_link)
    if site == "CodeChef":
        return _retrieve_codechef_submission(view_link)
    elif site == "CodeForces":
        return _retrieve_codeforces_submission(view_link)
    else:
        return -1

# ----------------------------------------------------------------------------
@auth.requires_login()
def unfriend():
    """
        Unfriend the user
    """

    if len(request.args) != 1:
        return "Please click on a button!"
    else:
        friend_id = long(request.args[0])
        user_id = session.user_id
        ftable = db.friends

        # Delete records in the friends table
        query = (ftable.user_id == user_id) & (ftable.friend_id == friend_id)
        value = db(query).count()
        if value == 0:
            return "Invalid URL"

        db(query).delete()
        query = (ftable.user_id == friend_id) & (ftable.friend_id == user_id)
        db(query).delete()

        # Send email to the friend notifying about the tragedy ;)
        atable = db.auth_user
        row = db(atable.id == friend_id).select(atable.email).first()
        current.send_mail(to=row.email,
                          subject="A friend unfriended you on StopStalk",
                          message="""<html>
%s (%s) unfriended you on StopStalk <br />

To stop receiving mails - <a href="%s">Unsubscribe</a></html>
                                  """ % (session.handle,
                                         URL("user",
                                             "profile",
                                             args=[session.handle],
                                             scheme=True,
                                             host=True,
                                             extension=False),
                                         URL("default", "unsubscribe",
                                             scheme=True,
                                             host=True,
                                             extension=False)),
                          mail_type="unfriend")

        return "Successfully unfriended"

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

    cftable = db.custom_friend
    ftable = db.friends
    stable = db.submission
    atable = db.auth_user

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
    total_count = db(query).count()

    PER_PAGE = current.PER_PAGE
    count = total_count / PER_PAGE
    if total_count % PER_PAGE:
        count += 1

    if request.extension == "json":
        return dict(count=count,
                    total_rows=1)

    user = session.auth.user
    db.sessions_today.insert(message="%s %s %d %s" % (user.first_name,
                                                      user.last_name,
                                                      user.id,
                                                      datetime.datetime.now()))

    offset = PER_PAGE * (active - 1)
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

    if auth.is_logged_in() and request.post_vars:
        if request.post_vars.stickers is not None:
            response.flash = "Fill your address!"
            user = session.auth.user
            stickers = eval(request.post_vars["stickers"])
            if stickers[0] == 0:
                session.flash = "No claimable stickers"
                redirect(URL("default", "my_friends"))
            ctable.email.default = user.email
            ctable.name.default = user.first_name + " " + user.last_name
            ctable.subject.default = "Please send me stickers!"
            ctable.text_message.default = "My address is: "

    form = SQLFORM(ctable)

    if auth.is_logged_in():
        user = session.auth.user
        ctable.email.default = user.email

    if form.process().accepted:
        session.flash = "We will get back to you!"
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
        response.flash = "Please fill all the fields!"

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
