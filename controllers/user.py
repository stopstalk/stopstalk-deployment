import utilities
import time
from datetime import datetime, date

# -------------------------------------------------------------------------------
@auth.requires_login()
def index():
    return dict()

# -------------------------------------------------------------------------------
def get_dates():
    """
        Return a dictionary containing count of submissions
        on each date
    """

    if len(request.args) < 1:
        if session.handle:
            handle = str(session.handle)
        else:
            redirect(URL("default", "index"))
    else:
        handle = str(request.args[0])

    sql_query = """
                    SELECT status, time_stamp, COUNT(*)
                    FROM submission
                    WHERE submission.stopstalk_handle=
                """

    sql_query += "'" + handle + "' "
    sql_query += "GROUP BY DATE(submission.time_stamp), submission.status;"
    row = db.executesql(sql_query)

    total_submissions = {}
    streak = max_streak = 0
    prev = curr = start = None

    for i in row:

        if prev is None and streak == 0:
            prev = time.strptime(str(i[1]), "%Y-%m-%d %H:%M:%S")
            prev = date(prev.tm_year, prev.tm_mon, prev.tm_mday)
            streak = 1
            start = prev
        else:
            curr = time.strptime(str(i[1]), "%Y-%m-%d %H:%M:%S")
            curr = date(curr.tm_year, curr.tm_mon, curr.tm_mday)

            if (curr - prev).days == 1:
                streak += 1
            elif curr != prev:
                streak = 1

            prev = curr

        if streak > max_streak:
            max_streak = streak

        sub_date = str(i[1]).split()[0]
        if total_submissions.has_key(sub_date):
            total_submissions[sub_date][i[0]] = i[2]
            total_submissions[sub_date]["count"] += i[2]
        else:
            total_submissions[sub_date] = {}
            total_submissions[sub_date][i[0]] = i[2]
            total_submissions[sub_date]["count"] = i[2]

    today = datetime.today().date()

    # Check if the last streak is continued till today
    if (today - prev).days > 1:
        streak = 0

    return dict(total=total_submissions,
                max_streak=max_streak,
                curr_streak=streak)

# -------------------------------------------------------------------------------
def get_stats():
    """
        Get statistics of the user
    """

    if request.extension != "json":
        redirect(URL("default", "index"))

    if len(request.args) < 1:
        if session.handle:
            handle = str(session.handle)
        else:
            redirect(URL("default", "index"))
    else:
        handle = str(request.args[0])

    stable = db.submission
    count = stable.id.count()
    row = db(stable.stopstalk_handle == handle).select(stable.status, count,
                                                       groupby=stable.status)
    return dict(row=row)

# -------------------------------------------------------------------------------
def profile():
    """
        Controller to show user profile
    """

    if len(request.args) < 1:
        if session.handle:
            handle = str(session.handle)
        else:
            redirect(URL("default", "index"))
    else:
        handle = str(request.args[0])

    query = (db.auth_user.stopstalk_handle == handle)
    row = db(query).select().first()
    if row is None:
        row = db(db.custom_friend.stopstalk_handle == handle).select().first()

    stable = db.submission
    name = row.first_name + " " + row.last_name
    group_by = []
    query = stable.stopstalk_handle == handle
    rows = db(query).select(stable.site,
                            stable.status,
                            stable.id.count(),
                            groupby=[stable.site, stable.status])


    data = {}
    for site in current.SITES:
        data[site] = [0, 0]

    for i in rows:
        submission = i.as_dict()
        cnt = submission["_extra"]["COUNT(submission.id)"]
        status = submission["submission"]["status"]
        site = submission["submission"]["site"]

        if status == "AC":
            data[site][0] += cnt
        data[site][1] += cnt

    efficiency = {}
    for i in data:
        if data[i][0] == 0 or data[i][1] == 0:
            efficiency[i] = "-"
            continue
        else:
            efficiency[i] = "%.3f" % (data[i][0] * 100.0 / data[i][1])

    return dict(name=name,
                efficiency=efficiency,
                handle=handle)

# -------------------------------------------------------------------------------
def submissions():
    """
        Retrieve submissions of a specific user
        @ToDo: Bootstrap Pagination
    """

    custom = False

    if len(request.args) < 1:
        user_id = session.user_id
    else:
        query = (db.auth_user.stopstalk_handle == request.args[0])
        row = db(query).select().first()
        if row:
            user_id = row.id
        else:
            query = (db.custom_friend.stopstalk_handle == request.args[0])
            row = db(query).select().first()
            if row:
                user_id = row.id
                custom = True
            else:
                redirect(URL("default", "index"))

    stable = db.submission
    utilities.retrieve_submissions(user_id, custom)

    if custom:
        query = (stable.custom_user_id == user_id)
    else:
        query = (stable.user_id == user_id)

    all_submissions = db(query).select(orderby=~stable.time_stamp)
    table = utilities.render_table(all_submissions)

    return dict(table=table)

# -------------------------------------------------------------------------------
@auth.requires_login()
def friend_requests():
    """
        Show friend requests to the logged-in user
    """

    rows = db(db.friend_requests.to_h == session.user_id).select()
    table = TABLE(_class="table")
    table.append(TR(TH(T("Name")),
                    TH(T("Institute")),
                    TH(T("Action"))))

    for row in rows:
        tr = TR()
        tr.append(TD(row.from_h.first_name + " " + row.from_h.last_name))
        tr.append(TD(row.from_h.institute))
        tr.append(TD(FORM(INPUT(_value="Accept", _type="submit"),
                          _action=URL("user", "accept_fr",
                                      args=[row.from_h, row.id])),
                     FORM(INPUT(_value="Reject", _type="submit"),
                          _action=URL("user", "reject_fr", args=[row.id])),
                     ))
        table.append(tr)

    return dict(table=table)

# -------------------------------------------------------------------------------
@auth.requires_login()
def add_friend(user_id, friend_id):
    """
        Add a friend into friend-list
    """

    query = (db.friends.user_id == user_id)
    user_friends = db(query).select(db.friends.friends_list).first()

    user_friends = eval(user_friends["friends_list"])
    user_friends.add(friend_id)

    db(query).update(friends_list=str(user_friends))

# -------------------------------------------------------------------------------
@auth.requires_login()
def accept_fr():
    """
        Helper function to accept friend request
    """

    if len(request.args) < 2:
        redirect(URL("user", "friend_requests"))

    friend_id = int(request.args[0])
    row_id = int(request.args[1])
    user_id = session.user_id

    # Add friend ID to user's friends list
    add_friend(user_id, friend_id)

    # Add user ID to friend's friends list
    add_friend(friend_id, user_id)

    # Delete the friend request row
    db(db.friend_requests.id == row_id).delete()

    redirect(URL("user", "friend_requests"))
    return dict()

# -------------------------------------------------------------------------------
@auth.requires_login()
def reject_fr():
    """
        Helper function to reject friend request
    """

    if request.args == []:
        redirect(URL("user", "friend_requests"))

    fr_id = request.args[0]

    # Simply delete the friend request
    db(db.friend_requests.id == fr_id).delete()

    redirect(URL("user", "friend_requests"))
    return dict()

# -------------------------------------------------------------------------------
@auth.requires_login()
def custom_friend():
    """
        Controller to add a Custom Friend
    """

    list_fields = ["first_name",
                   "last_name",
                   "institute",
                   "stopstalk_handle"]

    for site in current.SITES:
        list_fields += [site.lower() + "_handle"]

    form = SQLFORM(db.custom_friend,
                   fields=list_fields,
                   hidden=dict(user_id=session.user_id,
                               last_retrieved=datetime.now()))

    # Set the hidden field
    form.vars.user_id = session.user_id
    form.process()

    if form.accepted:
        session.flash = "Submissions for custom user added"
        redirect(URL("default", "submissions", args=[1]))
    return dict(form=form)
