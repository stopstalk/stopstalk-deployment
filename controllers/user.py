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

import utilities
import time
import datetime

# ------------------------------------------------------------------------------
@auth.requires_login()
def index():
    """
        Not used
    """

    return dict()

# ------------------------------------------------------------------------------
@auth.requires_login()
def add_custom_friend():
    """
        Add an already existing custom user to some other user
    """

    post_vars = request.post_vars
    atable = db.auth_user
    cftable = db.custom_friend
    stopstalk_handle = post_vars["stopstalk_handle"]
    # Modify(Prepare) this dictionary for inserting it again
    # @ToDo: Need a better method. Major security flaw
    current_row = eval(post_vars["row"])
    original_handle = current_row["stopstalk_handle"]

    stopstalk_handles = []
    rows = db(atable).select(atable.stopstalk_handle)
    rows = [x["stopstalk_handle"] for x in rows]
    stopstalk_handles.extend(rows)

    rows = db(cftable).select(cftable.stopstalk_handle)
    rows = [x["stopstalk_handle"] for x in rows]
    stopstalk_handles.extend(rows)

    for temp_handle in stopstalk_handles:
        if stopstalk_handle.lower() == temp_handle.lower():
            session.flash = "Handle already taken"
            redirect(URL("user", "profile", args=original_handle))

    # The total referrals by the logged-in user
    query = (atable.referrer == session["handle"])

    # User should not enter his/her own
    # stopstalk handle as referrer handle
    query &= (atable.stopstalk_handle != session["handle"])
    total_referrals = db(query).count()

    # Retrieve the total allowed custom users from auth_user table
    query = (atable.id == session["user_id"])
    row = db(query).select(atable.referrer,
                           atable.allowed_cu).first()
    default_allowed = row.allowed_cu
    referrer = 0
    # If a valid referral is applied then award 1 extra CU
    if row.referrer and row.referrer != session["handle"]:
        referrer = db(atable.stopstalk_handle == row.referrer).count()

    # 3 custom friends allowed plus one for each 5 invites

    allowed_custom_friends = total_referrals / 5 + default_allowed + referrer

    # Custom users already created
    current_count = db(db.custom_friend.user_id == session["user_id"]).count()

    if current_count >= allowed_custom_friends:
        session.flash = "Sorry!! All custom users used up!"
        redirect(URL("user", "profile", args=original_handle))

    # ID of the custom user
    original_id = long(current_row["id"])

    # Delete this id as this will be incremented
    # automatically on insert
    del current_row["id"]

    # Set duplicate_cu for this new user
    current_row["duplicate_cu"] = original_id
    # Set the user_id as current logged in user
    current_row["user_id"] = session.user_id
    # Update the stopstalk handle
    current_row["stopstalk_handle"] = stopstalk_handle

    # Insert a new Custom friend for the logged-in user
    cftable.insert(**current_row)

    session.flash = "Custom user added!!"
    redirect(URL("user", "profile", args=stopstalk_handle))

# ------------------------------------------------------------------------------
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
                                 args=[row.stopstalk_handle]),
                       _target="_blank")))
        tr.append(TD(row.stopstalk_handle))

        for site in current.SITES:
            tmp_handle = row[site.lower() + "_handle"]
            if tmp_handle:
                tr.append(TD(A(tmp_handle,
                               _href=current.SITES[site] + tmp_handle,
                               _target="_blank")))
            else:
                tr.append(TD())
        tr.append(TD(FORM(INPUT(_class="btn yellow",
                                _style="color: black;",
                                _value="Update",
                                _type="submit"),
                          _action=URL("user",
                                      "update_friend",
                                      args=[row.id]))))
        table.append(tr)

    return dict(table=table)

# ------------------------------------------------------------------------------
@auth.requires_login()
def update_details():
    """
        Update user details
    """

    form_fields = ["first_name",
                   "last_name",
                   "email",
                   "institute",
                   "stopstalk_handle"]

    for site in current.SITES:
        form_fields.append(site.lower() + "_handle")

    record = db.auth_user(session.user_id)
    form = SQLFORM(db.auth_user,
                   record,
                   fields=form_fields,
                   showid=False)

    if form.process().accepted:
        session.flash = "User details updated"
        atable = db.auth_user

        query = (atable.id == session.user_id)
        db(query).update(rating=0,
                         last_retrieved=current.INITIAL_DATE,
                         per_day=0.0)
        db(db.submission.user_id == session.user_id).delete()

        redirect(URL("default", "submissions", args=[1]))
    elif form.errors:
        response.flash = "Form has errors"

    return dict(form=form)

# ------------------------------------------------------------------------------
@auth.requires_login()
def update_friend():
    """
        Update custom friend details
    """

    if len(request.args) != 1:
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
                   deletable=True,
                   showid=False)

    if form.validate():
        if form.deleted:
            ## DELETE
            # If delete checkbox is checked => just process it redirect back
            session.flash = "Custom User deleted"
            db(cftable.id == record.id).delete()
            redirect(URL("user", "edit_custom_friend_details"))
        else:
            ## UPDATE
            # If delete checkbox is not checked
            updated_handles = False

            # Check if any of the site handle is updated
            for site in current.SITES:
                site_handle = site.lower() + "_handle"
                if record[site_handle] != form.vars[site_handle]:
                    updated_handles = True
                    break

            if updated_handles:
                form.vars["duplicate_cu"] = None
                # Since there may be some updates in the handle
                # for correctness we need to remove all the submissions
                # and retrieve all the submissions again(Will be updated next day)
                form.vars["last_retrieved"] = current.INITIAL_DATE
                form.vars["rating"] = 0
                form.vars["per_day"] = 0.0
                db(db.submission.custom_user_id == request.args[0]).delete()

            record.update_record(**dict(form.vars))

            session.flash = "User details updated"
            redirect(URL("user", "edit_custom_friend_details"))

    elif form.errors:
        response.flash = "Form has errors"

    return dict(form=form)

# ------------------------------------------------------------------------------
def get_dates():
    """
        Return a dictionary containing count of submissions
        on each date
    """

    if len(request.args) != 1:
        if session.handle:
            handle = str(session.handle)
        else:
            redirect(URL("default", "index"))
    else:
        handle = str(request.args[0])

    sql_query = """
                    SELECT status, time_stamp, COUNT(*)
                    FROM submission
                    WHERE submission.stopstalk_handle='%s'
                    GROUP BY DATE(submission.time_stamp), submission.status;
                """ % (handle)

    row = db.executesql(sql_query)
    total_submissions = {}

    # For day streak
    streak = max_streak = 0
    prev = curr = None

    # For accepted solutions streak
    curr_accepted_streak = utilities.get_accepted_streak(handle)
    max_accepted_streak = utilities.get_max_accepted_streak(handle)

    for i in row:

        if prev is None and streak == 0:
            prev = time.strptime(str(i[1]), "%Y-%m-%d %H:%M:%S")
            prev = datetime.date(prev.tm_year, prev.tm_mon, prev.tm_mday)
            streak = 1
        else:
            curr = time.strptime(str(i[1]), "%Y-%m-%d %H:%M:%S")
            curr = datetime.date(curr.tm_year, curr.tm_mon, curr.tm_mday)

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

    today = datetime.datetime.today().date()

    # Check if the last streak is continued till today
    if prev is None or (today - prev).days > 1:
        streak = 0

    return dict(total=total_submissions,
                max_streak=max_streak,
                curr_streak=streak,
                curr_accepted_streak=curr_accepted_streak,
                max_accepted_streak=max_accepted_streak)

# ------------------------------------------------------------------------------
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
    query = (stable.stopstalk_handle == handle)
    row = db(query).select(stable.status,
                           count,
                           groupby=stable.status)
    return dict(row=row)

# ------------------------------------------------------------------------------
def get_activity():

    if request.extension != "json":
        return dict(table="")
    stable = db.submission
    post_vars = request.post_vars
    date = post_vars["date"]
    if date is None:
        return dict(table="")
    handle = post_vars["handle"]
    start_time = date + " 00:00:00"
    end_time = date + " 23:59:59"

    query = (stable.time_stamp >= start_time)
    query &= (stable.time_stamp <= end_time)
    query &= (stable.stopstalk_handle == handle)
    submissions = db(query).select()

    if len(submissions) > 0:
        table = utilities.render_table(submissions)
        table = DIV(H3("Activity on " + date), table)
    else:
        table = H5("No activity on " + date)

    return dict(table=table)

# ------------------------------------------------------------------------------
def profile():
    """
        Controller to show user profile
        @ToDo: Lots of cleanup! Atleast run a lint
    """

    if len(request.args) < 1:
        if session.handle:
            handle = str(session.handle)
        else:
            redirect(URL("default", "index"))
    else:
        handle = str(request.args[0])

    query = (db.auth_user.stopstalk_handle == handle)
    rows = db(query).select()
    row = None
    flag = "not-friends"
    custom = False
    actual_handle = handle
    parent_user = None
    output = {}
    output["nouser"] = False

    if len(rows) == 0:
        query = (db.custom_friend.stopstalk_handle == handle)
        rows = db(query).select()
        if len(rows) == 0:
            # No such user exists
            return dict(nouser=True)
        else:
            flag = "custom"
            custom = True
            row = rows.first()
            parent_user = (row.user_id.first_name + " " + \
                                row.user_id.last_name,
                           row.user_id.stopstalk_handle)
            if row.duplicate_cu:
                flag = "duplicate-custom"
                original_row = db.custom_friend(row.duplicate_cu)
                actual_handle = row.stopstalk_handle
                handle = original_row.stopstalk_handle
                original_row["first_name"] = row.first_name
                original_row["last_name"] = row.last_name
                original_row["institute"] = row.institute
                original_row["user_id"] = row.user_id
                row = original_row
            output["row"] = row
    else:
        row = rows.first()
        output["row"] = row

    output["parent_user"] = parent_user
    output["handle"] = handle
    output["actual_handle"] = actual_handle
    name = row.first_name + " " + row.last_name
    output["name"] = name
    output["custom"] = custom

    stable = db.submission
    total_submissions = db(stable.stopstalk_handle == handle).count()
    output["total_submissions"] = total_submissions

    if custom:
        if row.user_id == session.user_id:
            flag = "my-custom-user"
    else:
        if row.id != session.user_id:
            ftable = db.friends
            frtable = db.friend_requests
            query = (ftable.user_id == session.user_id)
            query &= (ftable.friend_id == row.id)
            value = db(query).count()
            if value == 0:
                query = (frtable.from_h == session.user_id)
                query &= (frtable.to_h == row.id)
                query |= (frtable.from_h == row.id) & \
                         (frtable.to_h == session.user_id)

                value = db(query).count()
                if value != 0:
                    flag = "pending"
            else:
                flag = "already-friends"
        else:
            flag = "same-user"

    output["flag"] = flag

    group_by = [stable.site, stable.status]
    query = (stable.stopstalk_handle == handle)
    rows = db(query).select(stable.site,
                            stable.status,
                            stable.id.count(),
                            groupby=group_by)


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

    output["efficiency"] = efficiency

    return output

# ------------------------------------------------------------------------------
def submissions():
    """
        Retrieve submissions of a specific user
    """

    custom = False
    atable = db.auth_user
    cftable = db.custom_friend
    handle = None
    duplicates = []

    if len(request.args) < 1:
        if session.user_id:
            user_id = session.user_id
            handle = session.handle
        else:
            redirect(URL("default", "index"))
    else:
        handle = request.args[0]
        query = (atable.stopstalk_handle == handle)
        row = db(query).select(atable.id, atable.first_name).first()
        if row is None:
            query = (cftable.stopstalk_handle == handle)
            row = db(query).select().first()
            if row:
                custom = True
                if row.duplicate_cu:
                    duplicates = [(row.id, row.duplicate_cu)]
                    handle = row.duplicate_cu.stopstalk_handle
            else:
                redirect(URL("default", "index"))

    if request.vars["page"]:
        page = request.vars["page"]
    else:
        page = "1"

    stable = db.submission
    query = (stable.stopstalk_handle == handle)

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
    table = utilities.render_table(all_submissions, duplicates)

    if handle == session.handle:
        user = "Self"
    else:
        user = row["first_name"]

    return dict(handle=handle,
                user=user,
                table=table,
                total_rows=len(all_submissions))

# ------------------------------------------------------------------------------
@auth.requires_login()
def friend_requests():
    """
        Show friend requests to the logged-in user
    """

    rows = db(db.friend_requests.to_h == session.user_id).select()
    table = TABLE(_class="striped centered")
    table.append(THEAD(TR(TH(T("Name")),
                          TH(T("Institute")),
                          TH(T("Action")))))

    tbody = TBODY()
    for row in rows:
        tr = TR()
        tr.append(TD(A(row.from_h.first_name + " " + row.from_h.last_name,
                       _href=URL("user",
                                 "profile",
                                 args=[row.from_h.stopstalk_handle]),
                       _target="_blank")))
        tr.append(TD(row.from_h.institute))
        tr.append(TD(UL(LI(FORM(INPUT(_value="Accept",
                                      _type="submit",
                                      _class="btn",
                                      _style="background-color: green;"),
                                _action=URL("user", "accept_fr",
                                            args=[row.from_h, row.id]))),
                        LI(FORM(INPUT(_value="Reject",
                                      _type="submit",
                                      _class="btn",
                                      _style="background-color: red;"),
                                _action=URL("user", "reject_fr",
                                            args=[row.id]))),
                        _style="display: inline-flex; list-style-type: none;")))
        tbody.append(tr)

    table.append(tbody)
    return dict(table=table)

# -----------------------------------------------------------------------------
@auth.requires_login()
def add_friend(user_id, friend_id):
    """
        Add a friend into friend-list
    """

    db.friends.insert(user_id=user_id,
                      friend_id=friend_id)

# ------------------------------------------------------------------------------
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

    # Send acceptance email to the friend
    atable = db.auth_user
    row = db(atable.id == friend_id).select(atable.email).first()
    current.send_mail(row.email,
                      session.handle + \
                      " from StopStalk accepted your friend request!",
                      """
%s (%s) accepted your friend request

To stop receiving mails - %s
                      """ % (session.handle,
                             URL("user", "profile",
                                 args=[session.handle],
                                 scheme=True,
                                 host=True),
                             URL("default", "unsubscribe",
                                 scheme=True,
                                 host=True)))

    session.flash = "Friend added!"
    redirect(URL("user", "friend_requests"))

    return dict()

# ------------------------------------------------------------------------------
@auth.requires_login()
def reject_fr():
    """
        Helper function to reject friend request
    """

    if request.args == []:
        redirect(URL("user", "friend_requests"))

    fr_id = request.args[0]

    frtable = db.friend_requests
    atable = db.auth_user
    join_query = (frtable.from_h == atable.id)
    row = db(frtable.id == fr_id).select(atable.email,
                                         join=frtable.on(join_query)).first()
    # Simply delete the friend request
    db(db.friend_requests.id == fr_id).delete()

    # Send rejection email to the friend
    current.send_mail(row.email,
                      session.handle + \
                      " from StopStalk rejected your friend request!",
                      """
                         %s (%s) rejected your friend request

                         To stop receiving mails - %s
                      """ % (session.handle,
                             URL("user", "profile",
                                 args=[session.handle],
                                 scheme=True,
                                 host=True),
                             URL("default", "unsubscribe",
                                 scheme=True,
                                 host=True)))

    session.flash = "Friend request rejected!"
    redirect(URL("user", "friend_requests"))

# ------------------------------------------------------------------------------
@auth.requires_login()
def custom_friend():
    """
        Controller to add a Custom Friend
    """

    atable = db.auth_user

    # The total referrals by the logged-in user
    query = (atable.referrer == session["handle"])

    # User should not enter his/her own
    # stopstalk handle as referrer handle
    query &= (atable.stopstalk_handle != session["handle"])
    total_referrals = db(query).count()

    # Retrieve the total allowed custom users from auth_user table
    query = (atable.id == session["user_id"])
    row = db(query).select(atable.referrer,
                           atable.allowed_cu).first()
    default_allowed = row.allowed_cu
    referrer = 0
    # If a valid referral is applied then award 1 extra CU
    if row.referrer and row.referrer != session["handle"]:
        referrer = db(atable.stopstalk_handle == row.referrer).count()

    # 3 custom friends allowed plus one for each 5 invites
    allowed_custom_friends = total_referrals / 5 + default_allowed + referrer

    # Custom users already created
    current_count = db(db.custom_friend.user_id == session["user_id"]).count()

    if current_count >= allowed_custom_friends:
        return dict(form=None)

    list_fields = ["first_name",
                   "last_name",
                   "institute",
                   "stopstalk_handle"]

    for site in current.SITES:
        list_fields += [site.lower() + "_handle"]

    form = SQLFORM(db.custom_friend,
                   fields=list_fields,
                   hidden=dict(user_id=session.user_id))

    # Set the hidden field
    form.vars.user_id = session.user_id
    form.process(onvalidation=current.sanitize_fields)

    if form.accepted:
        session.flash = "Submissions will be added by tomorrow"
        redirect(URL("default", "submissions", args=[1]))

    return dict(form=form)

# END =========================================================================
