"""
    Copyright (c) 2015-2017 Raj Patel(raj454raj@gmail.com), StopStalk

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
def uva_handle():

    session.flash = T("Update your UVa handle")
    redirect(URL("user", "update_details"))

# ------------------------------------------------------------------------------
@auth.requires_login()
def friend_requests():
    """
        Just to avoid too many 404s
    """
    redirect(URL("default", "notifications"))

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
    rows = [x.stopstalk_handle for x in rows]
    stopstalk_handles.extend(rows)

    rows = db(cftable).select(cftable.stopstalk_handle)
    rows = [x.stopstalk_handle for x in rows]
    stopstalk_handles.extend(rows)

    for temp_handle in stopstalk_handles:
        if stopstalk_handle.lower() == temp_handle.lower():
            session.flash = T("Handle already taken")
            redirect(URL("user", "profile", args=original_handle))

    # The total referrals by the logged-in user
    query = (atable.referrer == session.handle)

    # User should not enter his/her own
    # stopstalk handle as referrer handle
    query &= (atable.stopstalk_handle != session.handle)
    total_referrals = db(query).count()

    # Retrieve the total allowed custom users from auth_user table
    query = (atable.id == session.user_id)
    row = db(query).select(atable.referrer,
                           atable.allowed_cu).first()
    default_allowed = row.allowed_cu
    referrer = 0
    # If a valid referral is applied then award 1 extra CU
    if row.referrer and row.referrer != session.handle:
        referrer = db(atable.stopstalk_handle == row.referrer).count()

    # 3 custom friends allowed plus one for each 3 invites

    allowed_custom_friends = total_referrals / 3 + default_allowed + referrer

    # Custom users already created
    current_count = db(db.custom_friend.user_id == session.user_id).count()

    if current_count >= allowed_custom_friends:
        session.flash = T("Sorry!! All custom users used up!")
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

    session.flash = T("Custom user added!!")
    redirect(URL("user", "profile", args=stopstalk_handle))

# ------------------------------------------------------------------------------
def get_graph_data():
    import os, pickle
    user_id = request.get_vars.get("user_id", None)
    custom = request.get_vars.get("custom", None)
    empty_dict = dict(graphs=[])
    if request.extension != "json":
        return empty_dict

    if user_id is None or custom is None:
        return empty_dict

    file_path = "./applications/%s/graph_data/%s" % (request.application,
                                                     user_id)
    if custom == "True":
        file_path += "_custom.pickle"
    else:
        file_path += ".pickle"
    if not os.path.exists(file_path):
        return empty_dict

    graph_data = pickle.load(open(file_path, "rb"))
    graphs = sum([graph_data[site.lower() + "_data"] for site in current.SITES], [])
    graphs = filter(lambda x: x["data"] != {}, graphs)

    return dict(graphs=graphs)

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
                   "country",
                   "stopstalk_handle"]

    for site in current.SITES:
        form_fields.append(site.lower() + "_handle")

    atable = db.auth_user
    stable = db.submission
    record = atable(session.user_id)

    # Do not allow to modify stopstalk_handle and email
    atable.stopstalk_handle.writable = False
    atable.stopstalk_handle.comment = T("StopStalk handle cannot be updated")

    atable.email.readable = True
    atable.email.writable = False
    atable.email.comment = T("Email cannot be updated")

    form = SQLFORM(db.auth_user,
                   record,
                   fields=form_fields,
                   showid=False)

    form.vars.email = record.email
    form.vars.stopstalk_handle = record.stopstalk_handle

    if form.process(onvalidation=current.sanitize_fields).accepted:
        session.flash = T("User details updated")

        updated_sites = utilities.handles_updated(record, form)
        if updated_sites != []:
            site_lrs = {}
            submission_query = (stable.user_id == session.user_id)
            for site in updated_sites:
                site_lrs[site.lower() + "_lr"] = current.INITIAL_DATE

            # Reset the user only if any of the profile site handle is updated
            query = (atable.id == session.user_id)
            db(query).update(rating=0,
                             prev_rating=0,
                             per_day=0.0,
                             per_day_change="0.0",
                             authentic=False,
                             **site_lrs)

            submission_query &= (stable.site.belongs(updated_sites))
            # Only delete the submission of those particular sites
            # whose site handles are updated
            db(submission_query).delete()

        session.auth.user = db.auth_user(session.user_id)
        redirect(URL("default", "submissions", args=[1]))
    elif form.errors:
        response.flash = T("Form has errors")

    return dict(form=form)

# ------------------------------------------------------------------------------
@auth.requires_login()
def update_friend():
    """
        Update custom friend details
    """

    if len(request.args) != 1:
        session.flash = T("Please click one of the buttons")
        redirect(URL("user", "custom_friend"))

    cftable = db.custom_friend
    stable = db.submission

    query = (cftable.user_id == session.user_id) & \
            (cftable.id == request.args[0])
    row = db(query).select(cftable.id)
    if len(row) == 0:
        session.flash = T("Please click one of the buttons")
        redirect(URL("user", "custom_friend"))

    record = cftable(request.args[0])

    # Do not allow to modify stopstalk_handle
    cftable.stopstalk_handle.writable = False

    form_fields = ["first_name",
                   "last_name",
                   "institute",
                   "country",
                   "stopstalk_handle"]

    for site in current.SITES:
        form_fields.append(site.lower() + "_handle")

    form = SQLFORM(cftable,
                   record,
                   fields=form_fields,
                   deletable=True,
                   showid=False)

    form.vars.stopstalk_handle = record.stopstalk_handle

    if form.validate(onvalidation=current.sanitize_fields):
        if form.deleted:
            ## DELETE
            # If delete checkbox is checked => just process it redirect back
            session.flash = T("Custom User deleted")
            duplicate_cus = db(cftable.duplicate_cu == record.id).select()
            if len(duplicate_cus):
                # The current custom user is a parent of other duplicate custom users

                first_dcu = duplicate_cus.first()

                # Populate stopstalk_handle of first child to submission tabls
                squery = (stable.stopstalk_handle == record.stopstalk_handle)
                db(squery).update(stopstalk_handle=first_dcu.stopstalk_handle)

                # Pick the first cu child and copy the stopstalk_handle to the parent
                record.update_record(user_id=first_dcu.user_id,
                                     stopstalk_handle=first_dcu.stopstalk_handle,
                                     institute=first_dcu.institute)
                # Now delete the first child as the parent is now modified
                # and the previous siblings remain as child to this parent
                first_dcu.delete_record()
            else:
                record.delete_record()
            redirect(URL("user", "custom_friend"))
        else:
            updated_sites = utilities.handles_updated(record, form)
            ## UPDATE
            if updated_sites != []:

                submission_query = (stable.custom_user_id == int(request.args[0]))
                reset_sites = current.SITES if record.duplicate_cu else updated_sites
                for site in reset_sites:
                    form.vars[site.lower() + "_lr"] = current.INITIAL_DATE

                submission_query &= (stable.site.belongs(reset_sites))

                form.vars["duplicate_cu"] = None
                form.vars["rating"] = 0
                form.vars["prev_rating"] = 0
                form.vars["per_day"] = 0.0
                form.vars["per_day_change"] = "0.0"

                # Only delete the submission of those particular sites
                # whose site handles are updated
                db(submission_query).delete()

            record.update_record(**dict(form.vars))

            session.flash = T("User details updated")
            redirect(URL("user", "custom_friend"))

    elif form.errors:
        response.flash = T("Form has errors")

    return dict(form=form)

# ------------------------------------------------------------------------------
def get_dates():
    """
        Return a dictionary containing count of submissions
        on each date
    """

    if request.vars.user_id and request.vars.custom:
        user_id = int(request.vars.user_id)
        custom = (request.vars.custom == "True")
    else:
        raise HTTP(400, "Bad request")
        return

    if custom:
        attribute = "submission.custom_user_id"
    else:
        attribute = "submission.user_id"

    sql_query = """
                    SELECT status, time_stamp, COUNT(*)
                    FROM submission
                    WHERE %s=%d
                    GROUP BY DATE(submission.time_stamp), submission.status;
                """ % (attribute, user_id)

    row = db.executesql(sql_query)
    total_submissions = {}

    # For day streak
    streak = max_streak = 0
    prev = curr = None

    # For accepted solutions streak
    curr_accepted_streak = utilities.get_accepted_streak(user_id, custom)
    max_accepted_streak = utilities.get_max_accepted_streak(user_id, custom)

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
def get_solved_counts():
    """
        Get the number of solved and attempted problems
    """

    if request.extension != "json" or \
       request.vars["user_id"] is None or \
       request.vars["custom"] is None:
        raise HTTP(400, "Bad request")
        return

    stable = db.submission
    if request.vars.custom == "True":
        query = (stable.custom_user_id == int(request.vars.user_id))
    elif request.vars.custom == "False":
        query = (stable.user_id == int(request.vars.user_id))
    else:
        return dict(total_problems=0, solved_problems=0)

    total_problems = db(query).count(distinct=stable.problem_link)
    query &= (stable.status == "AC")
    solved_problems = db(query).count(distinct=stable.problem_link)
    return dict(total_problems=total_problems, solved_problems=solved_problems)

# ------------------------------------------------------------------------------
def get_stats():
    """
        Get statistics of the user
    """

    if request.extension != "json":
        raise HTTP(400, "Bad request")
        return

    if request.vars.user_id and request.vars.custom:
        user_id = int(request.vars.user_id)
        custom = (request.vars.custom == "True")
    else:
        raise HTTP(400, "Bad request")
        return

    stable = db.submission
    count = stable.id.count()
    query = (stable.user_id == user_id)
    if custom:
        query = (stable.custom_user_id == user_id)
    row = db(query).select(stable.status,
                           count,
                           groupby=stable.status)
    return dict(row=row)

# ------------------------------------------------------------------------------
def get_activity():

    if request.extension != "json":
        return dict(table="")

    if request.vars.user_id and request.vars.custom:
        user_id = int(request.vars.user_id)
        custom = (request.vars.custom == "True")
    else:
        raise HTTP(400, "Bad request")
        return
        redirect(URL("default", "index"))

    stable = db.submission
    post_vars = request.post_vars
    date = post_vars["date"]
    if date is None:
        return dict(table="")
    start_time = date + " 00:00:00"
    end_time = date + " 23:59:59"

    query = (stable.time_stamp >= start_time) & \
            (stable.time_stamp <= end_time)

    if custom:
        query &= (stable.custom_user_id == user_id)
    else:
        query &= (stable.user_id == user_id)
    submissions = db(query).select(orderby=~stable.time_stamp)

    if len(submissions) > 0:
        table = utilities.render_table(submissions)
        table = DIV(H3(T("Activity on") + " " + date), table)
    else:
        table = H5(T("No activity on") + " " + date)

    return dict(table=table)

# ------------------------------------------------------------------------------
def handle_details():
    import json
    atable = db.auth_user
    cftable = db.custom_friend
    ihtable = db.invalid_handle
    handle = request.vars["handle"]

    row = db(atable.stopstalk_handle == handle).select().first()
    if row is None:
        row = db(cftable.stopstalk_handle == handle).select().first()
        if row is None:
            # Invalid handle in the get params
            return dict()

    query = False
    for site in current.SITES:
        query |= (ihtable.site == site) & \
                 (ihtable.handle == row[site.lower() + "_handle"])
    ihandles = db(query).select()
    invalid_sites = set([])
    for record in ihandles:
        # For case sensitive check of handles
        if record.handle == row[record.site.lower() + "_handle"]:
            invalid_sites.add(record.site)

    response = {}
    for site in current.SITES:
        smallsite = site.lower()
        # 1. Pending submission retrieval
        if str(row[smallsite + "_lr"]) == current.INITIAL_DATE:
            response[smallsite] = "pending-retrieval"
        # 2. Check for invalid handles
        if site in invalid_sites:
            response[smallsite] = "invalid-handle"
        # 3. Check for empty handles
        if row[smallsite + "_handle"] == "":
            response[smallsite] = "not-provided"

    return json.dumps(response)

# ------------------------------------------------------------------------------
def profile():
    """
        Controller to show user profile
        @ToDo: Lots of cleanup! Atleast run a lint
    """

    if len(request.args) < 1:
        if auth.is_logged_in():
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
            raise HTTP(404)
            return
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
                original_row["country"] = row.country
                original_row["user_id"] = row.user_id
                output["user_id"] = row.duplicate_cu
                row = original_row
            else:
                output["user_id"] = row.id
            output["row"] = row
    else:
        row = rows.first()
        output["user_id"] = row.id
        output["row"] = row

    last_updated = str(max([row[site.lower() + "_lr"] for site in current.SITES]))
    if last_updated == current.INITIAL_DATE:
        last_updated = "Never"
    output["last_updated"] = last_updated
    output["parent_user"] = parent_user
    output["handle"] = handle
    output["actual_handle"] = actual_handle
    name = row.first_name + " " + row.last_name
    output["name"] = name
    output["custom"] = custom

    stable = db.submission

    user_query = (stable.user_id == row.id)
    if custom:
        user_query = (stable.custom_user_id == row.id)
    total_submissions = db(user_query).count()

    output["total_submissions"] = total_submissions

    if custom:
        if row.user_id == session.user_id:
            flag = "my-custom-user"
    else:
        if row.id != session.user_id:
            ftable = db.following
            query = (ftable.follower_id == session.user_id) & \
                    (ftable.user_id == row.id)
            if db(query).count():
                flag = "already-friends"
        else:
            flag = "same-user"

    output["flag"] = flag

    rows = db(user_query).select(stable.site,
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

    output["efficiency"] = efficiency

    profile_urls = {}
    for site in current.SITES:
        profile_urls[site] = current.get_profile_url(site,
                                                     row[site.lower() + \
                                                         '_handle'])
    output["profile_urls"] = profile_urls
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
    row = None

    if len(request.args) < 1:
        if auth.is_logged_in():
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
                user_id = row.id
                if row.duplicate_cu:
                    duplicates = [(row.id, row.duplicate_cu)]
                    user_id = row.duplicate_cu.id
            else:
                raise HTTP(404)
                return
        else:
            user_id = row.id

    if request.vars["page"]:
        page = request.vars["page"]
    else:
        page = "1"

    stable = db.submission

    query = (stable.user_id == user_id)
    if custom:
        query = (stable.custom_user_id == user_id)

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
def custom_friend():
    """
        Controller to add a Custom Friend
    """

    atable = db.auth_user

    # The total referrals by the logged-in user
    query = (atable.referrer == session.handle) & \
            (atable.registration_key == "")

    # User should not enter his/her own
    # stopstalk handle as referrer handle
    query &= (atable.stopstalk_handle != session.handle)
    total_referrals = db(query).count()

    # Retrieve the total allowed custom users from auth_user table
    query = (atable.id == session.user_id)
    row = db(query).select(atable.referrer,
                           atable.allowed_cu).first()
    default_allowed = row.allowed_cu
    referrer = 0
    # If a valid referral is applied then award 1 extra CU
    if row.referrer and row.referrer != session.handle:
        query = (atable.stopstalk_handle == row.referrer) & \
                (atable.registration_key == "")
        referrer = db(query).count()

    # 3 custom friends allowed plus one for each 3 invites
    allowed_custom_friends = total_referrals / 3 + default_allowed + referrer

    # Custom users already created
    rows = db(db.custom_friend.user_id == session.user_id).select()

    table = TABLE(_class="bordered centered")
    tr = TR(TH(T("Name")),
            TH(T("StopStalk Handle")))

    tr.append(TH(T("Update")))
    table.append(THEAD(tr))

    tbody = TBODY()

    for row in rows:
        tr = TR()
        tr.append(TD(A(row.first_name + " " + row.last_name,
                       _href=URL("user",
                                 "profile",
                                 args=[row.stopstalk_handle]),
                       _target="_blank")))
        tr.append(TD(row.stopstalk_handle))

        tr.append(TD(FORM(INPUT(_class="btn yellow",
                                _style="color: black;",
                                _value=T("Update"),
                                _type="submit"),
                          _action=URL("user",
                                      "update_friend",
                                      args=[row.id]))))
        tbody.append(tr)

    table.append(tbody)
    if len(rows) >= allowed_custom_friends:
        return dict(form=None,
                    table=table,
                    allowed=allowed_custom_friends,
                    total_referrals=total_referrals)

    list_fields = ["first_name",
                   "last_name",
                   "institute",
                   "country",
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
        session.flash = T("Submissions will be added in some time")
        redirect(URL("default", "submissions", args=[1]))

    return dict(form=form,
                table=table,
                allowed=allowed_custom_friends,
                total_referrals=total_referrals)

# ==============================================================================
