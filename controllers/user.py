import utilities
import time
from datetime import datetime, date

# -------------------------------------------------------------------------------
@auth.requires_login()
def index():
    return dict()

# -------------------------------------------------------------------------------
@auth.requires_login()
def edit_custom_friend_details():
    """
        Edit Custom User details
    """

    cftable = db.custom_friend
    rows = db(cftable.user_id == session["user_id"]).select()

    table = TABLE(_class="table")
    tr = TR(TH("Name"),
            TH("StopStalk Handle"))

    for site in current.SITES:
        tr.append(TH(site + " Handle"))
    tr.append(TH("Update"))
    table.append(tr)

    for row in rows:
        tr = TR()
        tr.append(TD(A(row.first_name + " " + row.last_name,
                       _href=URL("user",
                                 "profile",
                                 args=[row.stopstalk_handle]))))
        tr.append(TD(row.stopstalk_handle))

        for site in current.SITES:
            tmp_handle = row[site.lower() + "_handle"]
            if tmp_handle:
                tr.append(TD(A(tmp_handle,
                               _href=current.SITES[site] + tmp_handle)))
            else:
                tr.append(TD())
        tr.append(TD(FORM(INPUT(_class="btn btn-warning",
                                _value="Update",
                                _type="submit"),
                          _action=URL("user", "update_friend", args=[row.id]))))
        table.append(tr)

    return dict(table=table)

# -------------------------------------------------------------------------------
@auth.requires_login()
def update_friend():

    if len(request.args) < 1:
        session.flash = "Please click one of the buttons"
        redirect(URL("user", "edit_custom_friend_details"))

    cftable = db.custom_friend

    query = (cftable.user_id == session["user_id"])
    query &= (cftable.id == request.args[0])
    row = db(query).select(cftable.id)
    if len(row) == 0:
        session.flash = "Please click one of the buttons"
        redirect(URL("user", "edit_custom_friend_details"))

    record = cftable(request.args[0])
    form_fields = ["first_name",
                   "last_name",
                   "institute",
                   "stopstalk_handle"]

    for site in current.SITES:
        form_fields.append(site.lower() + "_handle")

    form = SQLFORM(cftable,
                   record,
                   fields=form_fields,
                   deletable=True)

    if form.process().accepted:
        response.flash = "User details updated"
        db(cftable.id == request.args[0]).update(last_retrieved=current.INITIAL_DATE)
        db(db.submission.custom_user_id == request.args[0]).delete()
        redirect(URL("user", "edit_custom_friend_details"))
    elif form.errors:
        response.flash = "Form has errors"

    return dict(form=form)

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
        query = (db.custom_friend.stopstalk_handle == handle)
        row = db(query).select().first()

    stable = db.submission
    name = row.first_name + " " + row.last_name
    group_by = []
    query = (stable.stopstalk_handle == handle)
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
    """

    custom = False

    if len(request.args) < 1:
        if session.user_id:
            user_id = session.user_id
        else:
            redirect(URL("default", "index"))
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

    if request.vars["page"]:
        page = request.vars["page"]
    else:
        page = "1"

    stable = db.submission

    if custom:
        query = (stable.custom_user_id == user_id)
    else:
        query = (stable.user_id == user_id)

    PER_PAGE = current.PER_PAGE
    if request.extension == "json":
        total_submissions = db(query).count()
        page_count = total_submissions / PER_PAGE
        if total_submissions % PER_PAGE:
            page_count += 1
        return dict(page_count=page_count)

    offset = PER_PAGE * (int(page) - 1)
    all_submissions = db(query).select(orderby=~stable.time_stamp,
                                       limitby=(offset, offset + PER_PAGE))
    table = utilities.render_table(all_submissions)

    if user_id == session.user_id:
        user = "Self"
    else:
        user = row["first_name"]

    c = "0"
    if custom:
        c = "1"

    return dict(c=c,
                user=user,
                user_id=user_id,
                table=table)

# -------------------------------------------------------------------------------
@auth.requires_login()
def friend_requests():
    """
        Show friend requests to the logged-in user
    """

    rows = db(db.friend_requests.to_h == session.user_id).select()
    table = TABLE(_class="table table-condensed")
    table.append(TR(TH(T("Name")),
                    TH(T("Institute")),
                    TH(T("Action"))))

    for row in rows:
        tr = TR()
        tr.append(TD(row.from_h.first_name + " " + row.from_h.last_name))
        tr.append(TD(row.from_h.institute))
        tr.append(TD(UL(LI(FORM(INPUT(_value="Accept",
                                      _type="submit",
                                      _class="btn btn-success"),
                                _action=URL("user", "accept_fr",
                                            args=[row.from_h, row.id]))),
                        LI(FORM(INPUT(_value="Reject",
                                      _type="submit",
                                      _class="btn btn-danger"),
                                _action=URL("user", "reject_fr",
                                            args=[row.id]))),
                        _style="display: inline-flex;list-style-type: none;")))
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
