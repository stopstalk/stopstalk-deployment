import utilities
import time
from datetime import date
"""
    @ToDo: Loads of cleanup :D
"""

# -------------------------------------------------------------------------------
def index():
    """
        The main controller which redirects depending
        on the login status of the user and does some
        extra pre-processing
    """

    # If the user is logged in
    if session["auth"]:
        session["handle"] = session["auth"]["user"]["stopstalk_handle"]
        session["user_id"] = session["auth"]["user"]["id"]
        session.flash = "Logged in successfully"
        redirect(URL("default", "submissions", args=[1]))

    # Detect a registration has taken place
    # This will be the case when submission on
    # a register user form is done.
    row = db(db.auth_event.id > 0).select().last()
    if row:
        desc = row.description
    else:
        desc = ""

    # If the last auth_event record contains registered
    # or verification then retrieve submissions
    if desc.__contains__("Registered") or \
       desc.__contains__("Verification"):
        reg_user = desc.split(" ")[1]
        r = db(db.friends.user_id == reg_user).select()
        utilities.retrieve_submissions(int(reg_user))

        # User has a `set` of friends' ids
        # If user does not exists then initialize it with empty set
        if len(r) == 0:
            db.friends.insert(user_id=int(reg_user),
                              friends_list=str(set([])))

    response.flash = T("Please Login")
    return dict()

# -------------------------------------------------------------------------------
def get_max_streak(handle):
    """
        Get the maximum of all streaks

        @Todo: There is some bug here
    """

    row = db.executesql("SELECT time_stamp, COUNT(*) FROM submission WHERE submission.stopstalk_handle='" + handle + "' GROUP BY DATE(submission.time_stamp), submission.status;")

    streak = 0
    max_streak = 0
    prev = curr = start = None
    total_submissions = 0

    for i in row:
        total_submissions += i[1]
        if streak == 0:
            streak = 1
            prev = time.strptime(str(i[0]), "%Y-%m-%d %H:%M:%S")
            prev = date(prev.tm_year, prev.tm_mon, prev.tm_mday)
            start = prev
        else:
            curr = time.strptime(str(i[0]), "%Y-%m-%d %H:%M:%S")
            curr = date(curr.tm_year, curr.tm_mon, curr.tm_mday)
            delta = (curr - prev).days
            if delta == 1:
                streak += 1
            elif delta != 0:
                streak = 0
            prev = curr

        if streak > max_streak:
            max_streak = streak

    today = datetime.today().date()

    # If last streak does not match the current day
    if (today - start).days + 1 != streak:
        streak = 0

    return max_streak, total_submissions, streak

# -------------------------------------------------------------------------------
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
    row = db(ftable.user_id == session["user_id"]).select(ftable.friends_list).first()

    # Will contain list of handles of all the friends along
    # with the Custom Users added by the logged-in user
    handles = []

    for user in eval(row.friends_list):
        user_data = db(atable.id == user).select(atable.first_name,
                                                 atable.last_name,
                                                 atable.stopstalk_handle).first()

        handles.append((user_data.stopstalk_handle,
                        user_data.first_name + " " + user_data.last_name))

    # Check for streak of custom friends
    rows = db(ctable.user_id == session["user_id"]).select(ctable.first_name,
                                                           ctable.last_name,
                                                           ctable.stopstalk_handle)
    for user in rows:
        handles.append((user.stopstalk_handle,
                        user.first_name + " " + user.last_name))

    table = TABLE(_class="table")
    for handle in handles:
        max_streak, total_submissions, curr_streak = get_max_streak(handle[0])
        if curr_streak:
            tr = TR(TD(H3(A(handle[1],
                            _href=URL("user", "profile", args=[handle[0]])))),
                    TD(H3(str(curr_streak) + " ",
                       I(_class="fa fa-bolt",
                         _style="color:red"))
                       ))
    table.append(tr)

    return dict(table=table)

# -------------------------------------------------------------------------------
def compute_row(user, custom=False):
    """
        Computes rating and retrieves other
        information of the specified user
    """

    max_streak, total_submissions, curr_streak = get_max_streak(user.stopstalk_handle)
    query = (db.submission.stopstalk_handle == user.stopstalk_handle)
    query &= (db.submission.status == "AC")
    accepted = db(query).count()

    # Unique rating formula
    # @ToDo: Improvement is always better
    rating = max_streak * 100 + \
             total_submissions * 20 + \
             accepted * 5 + \
             (accepted * 100.0 / total_submissions) * 150 + \
             (total_submissions - accepted) * 1
    rating = int(rating)

    table = db.auth_user
    if custom:
        table = db.custom_friend

    # Update the rating whenever leaderboard page is loaded
    db(table.stopstalk_handle == user.stopstalk_handle).update(rating=rating)

    return (user.first_name + " " + user.last_name,
            user.stopstalk_handle,
            user.institute,
            rating)

# -------------------------------------------------------------------------------
def leaderboard():
    """
        Get a table with users sorted by rating
    """

    reg_users = db(db.auth_user.id > 0).select()
    custom_users = db(db.custom_friend.id > 0).select()

    users = []

    for user in reg_users:
        users.append(compute_row(user))

    for user in custom_users:
        users.append(compute_row(user, True))

    # Sort users according to the rating
    users = sorted(users, key=lambda x: x[3], reverse=True)

    table = TABLE(_class="table")

    table.append(TR(TH("Name"), TH("StopStalk Handle"), TH("Institute"), TH("StopStalk Rating")))
    for i in users:
        tr = TR()
        tr.append(TD(i[0]))
        tr.append(TD(A(i[1],
                     _href=URL("user", "profile", args=[i[1]]))))
        tr.append(TD(i[2]))
        tr.append(TD(i[3]))
        table.append(tr)

    return dict(table=table)

# -------------------------------------------------------------------------------
def user():
    return dict(form=auth())

# -------------------------------------------------------------------------------
@auth.requires_login()
def search():
    return dict()

# -------------------------------------------------------------------------------
@auth.requires_login()
def mark_friend():
    """
        Send a friend request
    """

    if len(request.args) < 1:
        session.flash = "Friend Request sent"
        redirect(URL("default", "search"))

    db.friend_requests.insert(from_h=session.user_id, to_h=request.args[0])
    session.flash = "Friend Request sent"
    redirect(URL("default", "search.html"))
    return dict()

# -------------------------------------------------------------------------------
@auth.requires_login()
def retrieve_users():
    """
        Show the list of registered users
    """

    q = request.get_vars.get("q", None)

    query = db.auth_user.first_name.like("%" + q + "%", case_sensitive=False)
    query |= db.auth_user.last_name.like("%" + q + "%", case_sensitive=False)
    query |= db.auth_user.stopstalk_handle.like("%" + q + "%", case_sensitive=False)

    for site in current.SITES:
        query |= db.auth_user[site.lower() + "_handle"].like("%" + q + "%", case_sensitive=False)

    # Don't show the logged in user in the search
    query &= (db.auth_user.id != session.user_id)
    rows = db(query).select()

    t = TABLE(_class="table")
    tr = TR(TH("Name"),
            TH("StopStalk Handle"),
            TH("Friendship Status"))

    for site in current.SITES:
        tr.append(TH(site + " Handle"))
    t.append(tr)

    for user in rows:

        friends = db(db.friends.user_id == user.id).select().first()
        friends = eval(friends.friends_list)
        tr = TR()
        tr.append(TD(user.first_name + " " + user.last_name))
        tr.append(TD(user.stopstalk_handle))

        for site in current.SITES:
            tr.append(TD(user[site.lower() + "_handle"]))

        # Check if the current user is already a friend or not
        if session.user_id not in friends:
            r = db((db.friend_requests.from_h == session.user_id) &
                   (db.friend_requests.to_h == user.id)).select()
            if len(r) == 0:
                tr.append(TD(FORM(INPUT(_type="submit",
                                        _value="Add Friend",
                                        _class="btn btn-warning"),
                                  _action=URL("default", "mark_friend",
                                              args=[user.id]))))
            else:
                tr.append(TD("Friend request sent"))
        else:
            tr.append(TD("Already friends"))
        t.append(tr)

    return dict(t=t)

# -------------------------------------------------------------------------------
@auth.requires_login()
def submissions():
    """
        Retrieve submissions of the logged-in user
    """

    if len(request.args) == 0:
        active = "1"
    else:
        active = request.args[0]

    custom_friends = db(db.custom_friend.user_id == session.user_id).select(db.custom_friend.id)

    cusfriends = []
    for f in custom_friends:
        cusfriends.append(f.id)

    # Get the friends of logged in user
    query = (db.friends.user_id == session.user_id)
    friends = db(query).select(db.friends.friends_list).first()
    friends = tuple(eval(friends.friends_list))

    query = (db.submission.user_id.belongs(friends))
    query |= (db.submission.custom_user_id.belongs(cusfriends))
    count = db(query).count()
    count = count / 100 + 1

    if request.extension == "json":
        return dict(count=count)

    if active == "1":
        for i in friends:
            utilities.retrieve_submissions(i)

        for i in cusfriends:
            utilities.retrieve_submissions(i, custom=True)

    rows = db(query).select(orderby=~db.submission.time_stamp,
                            limitby=(100 * (int(active) - 1), (int(active) - 1) * 100 + 100))

    table = utilities.render_table(rows)
    return dict(table=table)

# -------------------------------------------------------------------------------
def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()
