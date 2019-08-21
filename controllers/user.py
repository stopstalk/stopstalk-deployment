"""
    Copyright (c) 2015-2019 Raj Patel(raj454raj@gmail.com), StopStalk

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
import json

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
    # Modify (Prepare) this dictionary for inserting it again
    current_row = json.loads(post_vars["row"])
    original_handle = current_row["stopstalk_handle"]

    if not utilities.is_valid_stopstalk_handle(original_handle):
        session.flash = T("Expected alphanumeric (Underscore allowed)")
        redirect(URL("user", "profile", args=original_handle))
        return

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
    custom_user_id = cftable.insert(**current_row)
    current.create_next_retrieval_record(cftable(custom_user_id), True)

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

    custom = (custom == "True")

    stopstalk_handle = utilities.get_stopstalk_handle(user_id, custom)
    redis_cache_key = "get_graph_data_" + stopstalk_handle

    # Check if data is present in REDIS
    data = current.REDIS_CLIENT.get(redis_cache_key)
    if data:
        return json.loads(data)

    file_path = "./applications/%s/graph_data/%s" % (request.application,
                                                     user_id)
    if custom:
        file_path += "_custom.pickle"
    else:
        file_path += ".pickle"
    if not os.path.exists(file_path):
        return empty_dict

    graph_data = pickle.load(open(file_path, "rb"))
    graphs = []
    for site in current.SITES:
        lower_site = site.lower()
        if graph_data.has_key(lower_site + "_data"):
            graphs.extend(graph_data[lower_site + "_data"])
    graphs = filter(lambda x: x["data"] != {}, graphs)

    data = dict(graphs=graphs)
    current.REDIS_CLIENT.set(redis_cache_key,
                             json.dumps(data, separators=(",", ":")),
                             ex=1 * 60 * 60)
    return data

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
            utilities.clear_profile_page_cache(record.stopstalk_handle)
            site_lrs = {}
            nrtable = db.next_retrieval
            submission_query = (stable.user_id == session.user_id)
            nrtable_record = db(nrtable.user_id == session.user_id).select().first()
            if nrtable_record is None:
                nid = nrtable.insert(user_id=session.user_id)
                nrtable_record = nrtable(nid)
            for site in updated_sites:
                site_lrs[site.lower() + "_lr"] = current.INITIAL_DATE
                nrtable_record.update({site.lower() + "_delay": 0})

            nrtable_record.update_record()

            pickle_file_path = "./applications/stopstalk/graph_data/" + \
                               str(session.user_id) + ".pickle"
            import os
            if os.path.exists(pickle_file_path):
                os.remove(pickle_file_path)

            # Reset the user only if any of the profile site handle is updated
            query = (atable.id == session.user_id)
            db(query).update(stopstalk_rating=0,
                             stopstalk_prev_rating=0,
                             per_day=0.0,
                             per_day_change="0.0",
                             authentic=False,
                             graph_data_retrieved=False,
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
    record = db(query).select().first()
    if record is None:
        session.flash = T("Please click one of the buttons")
        redirect(URL("user", "custom_friend"))

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
        pickle_file_path = "./applications/stopstalk/graph_data/" + \
                           str(record.id) + "_custom.pickle"
        import os
        utilities.clear_profile_page_cache(record.stopstalk_handle)

        if form.deleted:
            ## DELETE
            # If delete checkbox is checked => just process it redirect back
            session.flash = T("Custom User deleted")
            duplicate_cus = db(cftable.duplicate_cu == record.id).select()
            if os.path.exists(pickle_file_path):
                os.remove(pickle_file_path)
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
                if os.path.exists(pickle_file_path):
                    os.remove(pickle_file_path)
                submission_query = (stable.custom_user_id == int(request.args[0]))
                reset_sites = current.SITES if record.duplicate_cu else updated_sites

                nrtable = db.next_retrieval
                nrtable_record = db(db.next_retrieval.custom_user_id == int(request.args[0])).select().first()
                if nrtable_record is None:
                    nid = nrtable.insert(custom_user_id=int(request.args[0]))
                    nrtable_record = nrtable(nid)
                for site in reset_sites:
                    form.vars[site.lower() + "_lr"] = current.INITIAL_DATE
                    nrtable_record.update({site.lower() + "_delay": 0})

                nrtable_record.update_record()

                submission_query &= (stable.site.belongs(reset_sites))

                form.vars["duplicate_cu"] = None
                form.vars["stopstalk_rating"] = 0
                form.vars["stopstalk_prev_rating"] = 0
                form.vars["per_day"] = 0.0
                form.vars["per_day_change"] = "0.0"
                form.vars["graph_data_retrieved"] = False

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
def get_activity():

    if request.extension != "json" or \
       request.vars.user_id is None or \
       request.vars.custom is None:
        raise HTTP(400, "Bad request")
        return

    user_id = int(request.vars.user_id)
    custom = (request.vars.custom == "True")

    stable = db.submission
    uetable = db.user_editorials

    post_vars = request.post_vars
    date = post_vars["date"]
    if date is None:
        return dict(table="")
    start_time = date + " 00:00:00"
    end_time = date + " 23:59:59"

    query = (stable.time_stamp >= start_time) & \
            (stable.time_stamp <= end_time)

    ue_query = (uetable.added_on >= start_time) & \
               (uetable.added_on <= end_time)

    if custom is False and auth.is_logged_in() and session.user_id == user_id:
        ue_query &= True
    else:
        ue_query &= (uetable.verification == "accepted")

    if custom:
        query &= (stable.custom_user_id == user_id)
        ue_query &= False
    else:
        query &= (stable.user_id == user_id)
        ue_query &= (uetable.user_id == user_id)

    submissions = db(query).select(orderby=~stable.time_stamp)
    user_editorials = db(ue_query).select(orderby=~uetable.id)
    editorials_table = utilities.render_user_editorials_table(user_editorials,
                                                              user_id,
                                                              session.user_id if auth.is_logged_in() else None,
                                                              "read-editorial-user-profile-page")

    if len(submissions) > 0 or len(user_editorials):
        div_element = DIV(H3(T("Activity on") + " " + date))
        if len(submissions) > 0:
            table = utilities.render_table(submissions, [], session.user_id)
            div_element.append(table)

            if len(user_editorials) > 0:
                div_element.append(BR())

        if len(user_editorials) > 0:
            div_element.append(editorials_table)
    else:
        div_element = H5(T("No activity on") + " " + date)

    return dict(table=div_element)

# ------------------------------------------------------------------------------
@auth.requires_login()
def mark_read():
    ratable = db.recent_announcements
    rarecord = db(ratable.user_id == session.user_id).select().first()
    if rarecord is None:
        ratable.insert(user_id=session.user_id)
        rarecord = db(ratable.user_id == session.user_id).select().first()
    data = json.loads(rarecord.data)
    data[request.vars.key] = True
    rarecord.update_record(data=json.dumps(data, separators=(",", ":")))
    return dict()

# ------------------------------------------------------------------------------
def handle_details():
    atable = db.auth_user
    cftable = db.custom_friend
    ihtable = db.invalid_handle
    handle = request.vars.handle

    row = db(atable.stopstalk_handle == handle).select().first()
    if row is None:
        row = db(cftable.stopstalk_handle == handle).select().first()
        if row is None:
            # Invalid handle in the get params
            return dict()

    redis_cache_key = "handle_details_" + row.stopstalk_handle

    # Check if data is present in REDIS
    data = current.REDIS_CLIENT.get(redis_cache_key)
    if data:
        return data

    query = False
    for site in current.SITES:
        query |= ((ihtable.site == site) & \
                  (ihtable.handle == row[site.lower() + "_handle"]))
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

    result = json.dumps(response, separators=(",", ":"))
    current.REDIS_CLIENT.set(redis_cache_key,
                             result,
                             ex=24 * 60 * 60)
    return result

# ------------------------------------------------------------------------------
def get_solved_unsolved():

    if request.extension != "json" or \
       request.vars.user_id is None or \
       request.vars.custom is None:
        raise HTTP(400, "Bad request")
        return

    user_id = int(request.vars.user_id)
    custom = (request.vars.custom == "True")

    solved_problems, unsolved_problems = utilities.get_solved_problems(user_id, custom)
    if auth.is_logged_in() and session.user_id == user_id and not custom:
        user_solved_problems, user_unsolved_problems = solved_problems, unsolved_problems
    else:
        if auth.is_logged_in():
            user_solved_problems, user_unsolved_problems = utilities.get_solved_problems(session.user_id, False)
        else:
            user_solved_problems, user_unsolved_problems = set([]), set([])


    solved_ids, unsolved_ids = [], []
    ptable = db.problem
    sttable = db.suggested_tags
    ttable = db.tag
    all_tags = db(ttable).select()
    all_tags = dict([(tag.id, tag.value) for tag in all_tags])

    query = ptable.id.belongs(solved_problems.union(unsolved_problems))
    # id => [problem_link, problem_name, problem_class]
    # problem_class =>
    #    0 (Logged in user has solved the problem)
    #    1 (Logged in user has attemted the problem)
    #    2 (User not logged in or not attempted the problem)
    problem_details = {}
    pids = []
    for problem in db(query).select(ptable.id, ptable.link, ptable.name):
        pids.append(problem.id)

        problem_status = 2
        if problem.id in user_unsolved_problems:
            # Checking for unsolved first because most of the problem links
            # would be found here instead of a failed lookup in solved_problems
            problem_status = 1
        elif problem.id in user_solved_problems:
            problem_status = 0

        problem_details[problem.id] = [problem.link, problem.name, problem_status, problem.id]

        if problem.id in solved_problems:
            solved_ids.append(problem.id)
        else:
            unsolved_ids.append(problem.id)

    problem_tags = {}
    query = (sttable.problem_id.belongs(pids)) & \
            (sttable.user_id == 1)
    for prow in db(query).select(sttable.tag_id, sttable.problem_id):
        if prow.problem_id not in problem_tags:
            problem_tags[prow.problem_id] = set([])
        problem_tags[prow.problem_id].add(prow.tag_id)

    categories = {"Dynamic Programming": set([1]),
                  "Greedy": set([28]),
                  "Strings": set([20]),
                  "Hashing": set([32]),
                  "Bit Manipulation": set([21, 42]),
                  "Trees": set([6, 9, 10, 11, 17, 31]),
                  "Graphs": set([4, 5, 15, 22, 23, 24, 26]),
                  "Algorithms": set([12, 14, 27, 29, 35, 36, 37, 38, 44, 51]),
                  "Data Structures": set([2, 3, 7, 8, 33, 34, 49]),
                  "Math": set([16, 30, 39, 40, 41, 43, 45, 50, 54]),
                  "Implementation": set([13, 18, 19]),
                  "Miscellaneous": set([46, 47, 48, 52])}
    ordered_categories = ["Dynamic Programming",
                          "Greedy",
                          "Strings",
                          "Hashing",
                          "Bit Manipulation",
                          "Trees",
                          "Graphs",
                          "Algorithms",
                          "Data Structures",
                          "Math",
                          "Implementation",
                          "Miscellaneous"]

    displayed_problems = set([])
    def _get_categorized_json(problem_ids):
        result = dict([(category, []) for category in ordered_categories])
        for pid in problem_ids:
            this_category = None
            if pid not in problem_tags:
                this_category = "Miscellaneous"
            else:
                ptags = problem_tags[pid]
                category_found = False
                for category in ordered_categories:
                    if len(categories[category].intersection(ptags)) > 0:
                        this_category = category
                        category_found = True
                        break
                if not category_found:
                    this_category = "Miscellaneous"
            pdetails = problem_details[pid]
            plink, pname, _, _ = pdetails
            psite = utilities.urltosite(plink)
            if (pname, psite) not in displayed_problems:
                displayed_problems.add((pname, psite))
                result[this_category].append(problem_details[pid])
        return result

    return dict(solved_problems=_get_categorized_json(solved_ids),
                unsolved_problems=_get_categorized_json(unsolved_ids),
                solved_html_widget=str(utilities.problem_widget("", "", "solved-problem", "Solved problem", None)),
                unsolved_html_widget=str(utilities.problem_widget("", "", "unsolved-problem", "Unsolved problem", None)),
                unattempted_html_widget=str(utilities.problem_widget("", "", "unattempted-problem", "Unattempted problem", None)))

# ------------------------------------------------------------------------------
def get_stopstalk_user_stats():
    if request.extension != "json":
        raise HTTP(400)
        return

    user_id = request.vars.get("user_id", None)
    custom = request.vars.get("custom", None)

    final_data = dict(
        rating_history=[],
        curr_accepted_streak=0,
        max_accepted_streak=0,
        curr_day_streak=0,
        max_day_streak=0,
        solved_counts={},
        status_percentages=[],
        site_accuracies={},
        solved_problems_count=0,
        total_problems_count=0,
        calendar_data={}
    )

    if user_id is None or custom is None:
        return final_data

    user_id = int(user_id)
    custom = (custom == "True")
    stopstalk_handle = utilities.get_stopstalk_handle(user_id, custom)
    redis_cache_key = "profile_page:user_stats_" + stopstalk_handle

    # Check if data is present in REDIS
    data = current.REDIS_CLIENT.get(redis_cache_key)
    if data:
        result = json.loads(data)
        if not auth.is_logged_in():
            del result["rating_history"]
        return result

    stable = db.submission

    query = (stable["custom_user_id" if custom else "user_id"] == user_id)
    rows = db(query).select(stable.time_stamp,
                            stable.problem_link,
                            stable.problem_id,
                            stable.status,
                            stable.site,
                            orderby=stable.time_stamp)

    # Returns rating history, accepted & max streak (day and accepted),
    result = utilities.get_stopstalk_user_stats(rows.as_list())

    if auth.is_logged_in():
        current.REDIS_CLIENT.set(redis_cache_key,
                                 json.dumps(result, separators=(",", ":")),
                                 ex=1 * 60 * 60)
    else:
        del result["rating_history"]

    return result

# ------------------------------------------------------------------------------
def profile():
    """
        Controller to show user profile
        @ToDo: Lots of cleanup! Atleast run a lint
    """
    if len(request.args) < 1:
        if auth.is_logged_in():
            handle = str(session.handle)
            redirect(URL("user", "profile", args=str(session.handle)))
            return
        else:
            redirect(URL("default", "user", "login",
                         vars={"_next": URL("user", "profile")}))
            return
    else:
        handle = str(request.args[0])
    http_referer = request.env.http_referer
    if auth.is_logged_in() and \
       session.welcome_shown is None and \
       http_referer is not None and \
       http_referer.__contains__("/user/login"):
       response.flash = T("Welcome StopStalker!!")
       session.welcome_shown = True

    query = (db.auth_user.stopstalk_handle == handle)
    rows = db(query).select()
    row = None
    flag = "not-friends"
    custom = False
    actual_handle = handle
    parent_user = None
    cf_count = 0
    cftable = db.custom_friend
    output = {}
    output["nouser"] = False
    output["show_refresh_now"] = False
    output["can_update"] = False

    if len(rows) == 0:
        query = (cftable.stopstalk_handle == handle)
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
                original_row = cftable(row.duplicate_cu)
                if auth.is_logged_in():
                    output["show_refresh_now"] = (row.user_id == session.user_id)
                output["can_update"] = (datetime.datetime.now() - row.refreshed_timestamp).total_seconds() > current.REFRESH_INTERVAL
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
                output["can_update"] = (datetime.datetime.now() - row.refreshed_timestamp).total_seconds() > current.REFRESH_INTERVAL
                if auth.is_logged_in():
                    output["show_refresh_now"] = (row.user_id == session.user_id)
                output["user_id"] = row.id
            output["row"] = row
    else:
        row = rows.first()
        output["user_id"] = row.id
        output["can_update"] = (datetime.datetime.now() - row.refreshed_timestamp).total_seconds() > current.REFRESH_INTERVAL
        output["row"] = row
        if auth.is_logged_in():
            output["show_refresh_now"] = (row.id == session.user_id)

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

    profile_urls = {}
    for site in current.SITES:
        profile_urls[site] = utilities.get_profile_url(site,
                                                       row[site.lower() + \
                                                           '_handle'])
    output["profile_urls"] = profile_urls
    if custom is False:
        cf_count = db(cftable.user_id == row.id).count()

    output["cf_count"] = cf_count

    return output

# ------------------------------------------------------------------------------
@auth.requires_login()
def add_to_refresh_now():
    custom = request.vars.get("custom", None)
    stopstalk_handle = request.vars.get("stopstalk_handle", None)
    if stopstalk_handle is None or custom is None:
        return "FAILURE"

    custom = (custom == "True")

    db_table = db.custom_friend if custom else db.auth_user
    nrtable = db.next_retrieval
    row = db(db_table.stopstalk_handle == stopstalk_handle).select().first()
    if row is None:
        return "FAILURE"

    authorized = False
    user_id = row.id
    if custom:
        authorized |= row.user_id == session.user_id
        user_id = row.duplicate_cu if row.duplicate_cu else row.id
    else:
        authorized |= row.id == session.user_id

    authorized &= (datetime.datetime.now() - row.refreshed_timestamp).total_seconds() > current.REFRESH_INTERVAL

    if not authorized:
        return "FAILURE"
    else:
        if custom:
            current.REDIS_CLIENT.rpush("next_retrieve_custom_user", user_id)
        else:
            current.REDIS_CLIENT.rpush("next_retrieve_user", user_id)

    row.update_record(refreshed_timestamp=datetime.datetime.now(),
                      graph_data_retrieved=False)
    update_params = {}
    for site in current.SITES:
        update_params[site.lower() + "_delay"] = 1
    if custom:
        db(nrtable.custom_user_id == user_id).update(**update_params)
    else:
        db(nrtable.user_id == user_id).update(**update_params)

    return "Successfully submitted request"

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

    if request.vars.page:
        page = request.vars.page
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
    table = utilities.render_table(all_submissions, duplicates, session.user_id)

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
        current.create_next_retrieval_record(form.vars, custom=True)
        redirect(URL("default", "submissions", args=[1]))

    return dict(form=form,
                table=table,
                allowed=allowed_custom_friends,
                total_referrals=total_referrals)

# ==============================================================================
