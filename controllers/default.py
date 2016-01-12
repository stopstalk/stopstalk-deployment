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
from datetime import date
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
def get_accepted_streak(handle):
    """
        Function that returns current streak of accepted solutions
    """
    sql_query = """
                SELECT COUNT( * )
                FROM  `submission`
                WHERE stopstalk_handle='%s'
                  AND time_stamp > (SELECT time_stamp
                                    FROM  `submission`
                                    WHERE stopstalk_handle='%s'
                                      AND STATUS <>  'AC'
                                    ORDER BY time_stamp DESC
                                    LIMIT 1)
                """ % (handle, handle)

    streak = db.executesql(sql_query)
    return streak[0][0]


# ----------------------------------------------------------------------------
def get_max_streak(handle):
    """
        Get the maximum of all streaks
    """

    # Build the complex SQL query
    sql_query = """
                    SELECT time_stamp, COUNT(*)
                    FROM submission
                    WHERE submission.stopstalk_handle=
                """

    sql_query += "'" + handle + "' "
    sql_query += """
                    GROUP BY DATE(submission.time_stamp), submission.status;
                 """

    row = db.executesql(sql_query)
    streak = 0
    max_streak = 0
    prev = curr = None
    total_submissions = 0

    for i in row:

        total_submissions += i[1]
        if prev is None and streak == 0:
            prev = time.strptime(str(i[0]), "%Y-%m-%d %H:%M:%S")
            prev = date(prev.tm_year, prev.tm_mon, prev.tm_mday)
            streak = 1
        else:
            curr = time.strptime(str(i[0]), "%Y-%m-%d %H:%M:%S")
            curr = date(curr.tm_year, curr.tm_mon, curr.tm_mday)

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

    return max_streak, total_submissions, streak, len(row)

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
    ctable = db.custom_friend

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
                        user.first_name + " " + user.last_name))

    # Check for streak of custom friends
    query = (ctable.user_id == session["user_id"])
    rows = db(query).select(ctable.first_name,
                            ctable.last_name,
                            ctable.stopstalk_handle)
    for user in rows:
        handles.append((user.stopstalk_handle,
                        user.first_name + " " + user.last_name))

    # List of users with non-zero streak
    users_on_streak = []

    for handle in handles:
        curr_streak = get_max_streak(handle[0])[2]
        curr_accepted_streak = get_accepted_streak(handle[0])

        # If streak is non-zero append to users_on_streak list
        if curr_streak:
            users_on_streak.append((handle, curr_streak, curr_accepted_streak))
        elif curr_accepted_streak:
            users_on_streak.append((handle, curr_streak, curr_accepted_streak))


    # Sort the users on streak by their streak
    users_on_streak.sort(key=lambda k: (k[1], k[2]), reverse=True)

    # The table containing users on streak
    table = TABLE(THEAD(TR(TH(STRONG("User")),
                           TH(STRONG("Days")),
                           TH(STRONG("Submissions")))),
                  _class="striped centered")

    tbody = TBODY()

    # Append all the users to the final table
    for users in users_on_streak:
        handle = users[0]
        curr_streak = users[1]
        curr_accepted_streak = users[2]
        tr = TR(TD((A(handle[1],
                      _href=URL("user", "profile", args=[handle[0]]),
                      _target="_blank"))),
                TD(str(curr_streak) + " ",
                   I(_class="fa fa-bolt",
                     _style="color:red"),
                   _class="center",
                   ),
                TD(str(curr_accepted_streak) + " ",
                   I(_class="fa fa-bolt",
                     _style="color:red"),
                   _class="center"))
        tbody.append(tr)

    table.append(tbody)
    return dict(table=table)

# ----------------------------------------------------------------------------
def compute_row(user, custom=False):
    """
        Computes rating and retrieves other
        information of the specified user
    """

    tup = get_max_streak(user.stopstalk_handle)
    max_streak = tup[0]
    total_submissions = tup[1]

    if total_submissions == 0:
        return ()

    stable = db.submission

    # Find the total solved problems(Lesser than total accepted)
    query = (stable.stopstalk_handle == user.stopstalk_handle)
    query &= (stable.status == "AC")
    solved = db(query).select(stable.problem_name, distinct=True)
    solved = len(solved)
    today = datetime.today().date()
    start = datetime.strptime(current.INITIAL_DATE,
                              "%Y-%m-%d %H:%M:%S").date()
    if custom:
        table = db.custom_friend
    else:
        table = db.auth_user

    query = (table.stopstalk_handle == user.stopstalk_handle)
    record = db(query).select().first()
    if record.per_day is None or \
       record.per_day == 0.0:
        per_day = total_submissions * 1.0 / (today - start).days
        db(query).update(per_day=per_day)

    else:
        row = db(query).select(table.per_day).first()
        per_day = row["per_day"]

    curr_per_day = total_submissions * 1.0 / (today - start).days
    diff = "%0.5f" % (curr_per_day - per_day)
    diff = float(diff)

    # I am not crazy. This is to solve the problem
    # if diff is -0.0
    if diff == 0.0:
        diff = 0.0

    # Unique rating formula
    # @ToDo: Improvement is always better
    rating = (curr_per_day - per_day) * 100000 + \
             max_streak * 50 + \
             solved * 100 + \
             (solved * 100.0 / total_submissions) * 40 + \
             (total_submissions - solved) * 10 + \
             per_day * 150

    rating = int(rating)

    table = db.auth_user
    if custom:
        table = db.custom_friend

    # Update the rating whenever leaderboard page is loaded
    db(table.stopstalk_handle == user.stopstalk_handle).update(rating=rating)

    return (user.first_name + " " + user.last_name,
            user.stopstalk_handle,
            user.institute,
            rating,
            diff,
            custom)

# ----------------------------------------------------------------------------
def leaderboard():
    """
        Get a table with users sorted by rating
    """

    specific_institute = False
    atable = db.auth_user
    cftable = db.custom_friend

    if request.vars.has_key("q"):
        institute = request.vars["q"]
        if institute != "":
            specific_institute = True
            reg_users = db(atable.institute == institute).select()
            custom_users = db(cftable.institute == institute).select()



    if specific_institute is False:
        reg_users = db(db.auth_user.id > 0).select()
        custom_users = db(db.custom_friend.id > 0).select()

    users = []

    for user in reg_users:
        tup = compute_row(user)
        if tup is not ():
            users.append(tup)

    for user in custom_users:
        tup = compute_row(user, True)
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
                          TH("Per Day Changes"))))

    tbody = TBODY()
    rank = 1
    for i in users:

        # If there are no submissions of the user in the database
        if i is ():
            continue

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

    all_languages = db(stable.id > 0).select(stable.lang,
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

    if session.auth:
        # Retrieve all the custom users created by the logged-in user
        query = (cftable.first_name.contains(get_vars["name"]))
        query |= (cftable.last_name.contains(get_vars["name"]))
        query &= (cftable.user_id == session.user_id)
        custom_friends = db(query).select(cftable.id)
        cusfriends = [x["id"] for x in custom_friends]

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

        # User in one of the friends
        query = (stable.user_id.belongs(friends))

        # User in one of the custom friends
        query |= (stable.custom_user_id.belongs(cusfriends))

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
        end_date = str(datetime.today())
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

    table = utilities.render_table(filtered)

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
    friend_id = request.args[0]

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
    db.friend_requests.insert(from_h=session.user_id, to_h=request.args[0])

    # Send the user an email notifying about the request
    atable = db.auth_user
    query = (atable.id == request.args[0])
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
                   (frtable.to_h == user.id)).select()
            if len(r) == 0:
                tr.append(TD(FORM(INPUT(_type="submit",
                                        _value="Add Friend",
                                        _class="btn waves-light waves-effect green"),
                                  _action=URL("default", "mark_friend",
                                              args=[user.id]))))
            else:
                tr.append(TD("Friend request sent"))
        else:
            tr.append(TD(FORM(INPUT(_type="submit",
                                    _value="Unfriend",
                                    _class="btn waves-light waves-effect red",
                                    ),
                              _action=URL("default", "unfriend", args=[user.id]))))
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
        friend_id = request.args[0]
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

    query = (stable.user_id.belongs(friends))
    query |= (stable.custom_user_id.belongs(cusfriends))
    total_count = db(query).count()

    PER_PAGE = current.PER_PAGE
    count = total_count / PER_PAGE
    if total_count % PER_PAGE:
        count += 1

    friend_query = (atable.id.belongs(friends))
    friends_list = db(friend_query).select(atable.id,
                                           atable.first_name,
                                           atable.last_name)
    all_friends = []
    for friend in friends_list:
        friend_name = friend["first_name"] + " " + friend["last_name"]
        all_friends.append([friend["id"],
                            friend_name])

    cusfriend_query = (cftable.id.belongs(cusfriends))
    cusfriends_list = db(cusfriend_query).select(cftable.id,
                                                 cftable.first_name,
                                                 cftable.last_name)
    all_custom_friends = []
    for friend in cusfriends_list:
        friend_name = friend["first_name"] + " " + friend["last_name"]
        all_custom_friends.append([friend["id"],
                                   friend_name])

    if request.extension == "json":
        return dict(count=count,
                    friends=all_friends,
                    cusfriends=all_custom_friends,
                    total_rows=1)

    offset = PER_PAGE * (int(active) - 1)
    # Retrieve only some number of submissions from the offset
    rows = db(query).select(orderby=~db.submission.time_stamp,
                            limitby=(offset, offset + PER_PAGE))

    table = utilities.render_table(rows)
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

    questions = ("What happens if I add a Custom User?",
                 "When can I update the submissions?",
                 "What if my friend is not on StopStalk?",
                 "How many Custom Users can I add?",
                 "How is the StopStalk rating determined?",
                 "What are per day changes?",
                 "What happens if someone accepts friend request?",
                 "Why can I see only some View buttons in the submissions table?",
                 "Can I view the StopStalk code?",
                 "Is there any tool which has extra features than the deployed version?",
                 "How should I refer to a friend?",
                 "Are there any benefits StopStalk provides for referring to a friend?",
                 "In what timezone are the submission times shown?",
                 "Why is my Institute listed in the dropdown?")

    answers = (MARKMIN("Custom User is a way to view submissions of a friend. Note: Only you can see his/her submissions"),
               MARKMIN("At present you can not explicitly update the submissions in the database. The submissions are automatically updated every morning."),
               MARKMIN("Best option is to ask him/her register on StopStalk and then send a friend request. If not, then you can add a Custom User if you already know all the handles."),
               MARKMIN("At present, the limit is set to 3 per user. We are working on it so that this limit is increased"),
               MARKMIN("StopStalk rating is determined by a very unique formula which takes care of number of solved problems, maximum streak, accuracy, per day changes and effort"),
               MARKMIN("Whenever user joins StopStalk, per day change is 0.0 and number of problems solved per day are computed. After every day this get modified depending on number of solutions submitted. Positive value says that you have benefitted after joining StopStalk"),
               MARKMIN("On accepting friend request both the user can see each others submissions"),
               MARKMIN("The sites that which allow to view anybody's submissions publicly have a View button. At present Codeforces and HackerEarth submissions can be viewed publicly"),
               MARKMIN("Yes, the code is completely open-sourced and it is on [[Github https://github.com/stopstalk/]]"),
               MARKMIN("Yes, there is the original version of the code with complete features [[here https://github.com/stopstalk/stopstalk/]] . You can set it up locally!"),
               MARKMIN("All you have to do is ask your friend to enter your StopStalk handle when asked for Referrer's StopStalk handle."),
               MARKMIN("Yes. You can increase the limit of number of custom users per user. At present 3 custom users are allowed on successful registration. On referring of 5 friends with your StopStalk handle you get 1 extra custom user."),
               MARKMIN("At present we are showing time stamps in IST(UTC +05:30), we are working on showing time stamps in the local timezone."),
               MARKMIN("We have limited number of Institutes at the present. Just fill \"Other\" in the Institute field and we will get back to you soon to confirm your Institute."))

    for i in xrange(len(questions)):
        li = LI(DIV(B(str(i + 1) + ". " + questions[i]),
                    _class="collapsible-header"),
                DIV(answers[i],
                    _class="collapsible-body"),
                )
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
                                  "Message: %s\n" % form.vars.text_message
                          )
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
