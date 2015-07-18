import profilesites as profile
from datetime import datetime
import time
import utilities

# -------------------------------------------------------------------------------
def get_submissions(user_id, handle, stopstalk_handle, submissions, site):
    """
        Get the submissions and populate the database
    """

    for i in sorted(submissions[handle].iterkeys()):
        for j in sorted(submissions[handle][i].iterkeys()):
            submission = submissions[handle][i][j]
            if len(submission) == 6:
                db.submission.insert(user_id=user_id,
                                     stopstalk_handle=stopstalk_handle,
                                     site_handle=handle,
                                     site=site,
                                     time_stamp=submission[0],
                                     problem_name=submission[2],
                                     problem_link=submission[1],
                                     lang=submission[5],
                                     status=submission[3],
                                     points=submission[4])

# -------------------------------------------------------------------------------
def retrieve_submissions(reg_user):
    """
        Retrieve submissions that are not already in the database
    """

    row = db(db.auth_user.id == reg_user).select().first()

    # Start retrieving from this date if user registered the first time
    initial_date = "2013-01-01 00:00:00"
    last_retrieved = db(db.submission.user_id == reg_user).select(orderby=~db.submission.time_stamp).first()
    if last_retrieved:
        last_retrieved = last_retrieved.time_stamp
    else:
        last_retrieved = initial_date

    last_retrieved = time.strptime(str(last_retrieved), "%Y-%m-%d %H:%M:%S")

    # ToDo: Make this generalized and extensible if a site is added
    if row.codechef_handle:

        handle = row.codechef_handle
        P = profile.Profile(codechef_handle=handle)
        submissions = P.codechef(last_retrieved)
        get_submissions(reg_user, handle, row.stopstalk_handle, submissions, "CodeChef")

    if row.codeforces_handle:

        handle = row.codeforces_handle
        P = profile.Profile(codeforces_handle=handle)
        submissions = P.codeforces(last_retrieved)
        get_submissions(reg_user, handle, row.stopstalk_handle, submissions, "CodeForces")

    if row.spoj_handle:
        handle = row.spoj_handle
        P = profile.Profile(spoj_handle=handle)
        submissions = P.spoj(last_retrieved)
        get_submissions(reg_user, handle, row.stopstalk_handle, submissions, "Spoj")

        
# -------------------------------------------------------------------------------
def index():

    if session["auth"]:
        session["handle"] = session["auth"]["user"]["stopstalk_handle"]
        session["user_id"] = session["auth"]["user"]["id"]
        session.flash = "Logged in successfully"
        redirect(URL("default", "submissions"))

    # Detect a registration has taken place
    row = db(db.auth_event.id > 0).select().last()
    if row:
        desc = row.description
    else:
        desc = ''
    if desc.__contains__("Registered") or desc.__contains__("Verification"):
        reg_user = desc.split(" ")[1]
        r = db(db.friends.user_id == reg_user).select()
        retrieve_submissions(int(reg_user))
        
        # User has a `set` of friends' ids
        # If user does not exists then initialize it with empty set
        if len(r) == 0:
            db.friends.insert(user_id=int(reg_user), friends_list=str(set([])))

    response.flash = T("Please Login")
    return dict()

# -------------------------------------------------------------------------------
def user():
    return dict(form=auth())

# -------------------------------------------------------------------------------
def search():
    return dict()

def mark_friend():
    if len(request.args) < 1:
        session.flash = "Friend Request sent"
        redirect(URL("default", "search"))

    db.friend_requests.insert(from_h=session.user_id, to_h=request.args[0])
    session.flash = "Friend Request sent"
    redirect(URL("default", "search.html"))
    return dict()
# -------------------------------------------------------------------------------
def retrieve_users():
    q = request.get_vars.get("q", None)
    
    # ToDo: improve this
    query = db.auth_user.first_name.like("%" + q + "%", case_sensitive=False)
    query |= db.auth_user.last_name.like("%" + q + "%", case_sensitive=False)
    query |= db.auth_user.stopstalk_handle.like("%" + q + "%", case_sensitive=False)
    query |= db.auth_user.codechef_handle.like("%" + q + "%", case_sensitive=False)
    query |= db.auth_user.codeforces_handle.like("%" + q + "%", case_sensitive=False)
    query |= db.auth_user.spoj_handle.like("%" + q + "%", case_sensitive=False)
    # Don't show the logged in user in the search
    query &= db.auth_user.id != session.user_id
    rows = db(query).select()

    t = TABLE(_class="table")
    tr = TR(TH("Name"),
            TH("StopStalk Handle"),
            TH("CodeChef Handle"),
            TH("CodeForces Handle"),
            TH("Spoj Handle"),
            TH("Friendship Status"))
    t.append(tr)

    for user in rows:

        friends = db(db.friends.user_id == user.id).select().first()
        friends = eval(friends.friends_list)
        tr = TR()
        tr.append(TD(user.first_name + " " + user.last_name))
        tr.append(TD(user.stopstalk_handle))
        tr.append(TD(user.codechef_handle))
        tr.append(TD(user.codeforces_handle))
        tr.append(TD(user.spoj_handle))
        if session.user_id not in friends:
            r = db((db.friend_requests.from_h == session.user_id) &
                   (db.friend_requests.to_h == user.id)).select()
            if len(r) == 0:
                tr.append(TD(FORM(INPUT(_type="submit", _value="Add Friend",
                                        _class="btn btn-warning"),
                                  _action=URL("default", "mark_friend", args=[user.id]))))
            else:
                tr.append(TD("Friend request sent"))
        else:
            tr.append(TD("Already friends"))
        t.append(tr)
    return dict(t=t)

# -------------------------------------------------------------------------------
@auth.requires_login()
def submissions():
    
    query = db.friends.user_id == session.user_id
    friends = db(query).select(db.friends.friends_list).first()
    friends = tuple(eval(friends.friends_list))
       
    query = db.submission.user_id.belongs(friends)
    rows = db(query).select(orderby=~db.submission.time_stamp)
    
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
