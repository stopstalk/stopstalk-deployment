import utilities
"""
    @ToDo: Loads of cleanup :D
"""
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
def user():
    return dict(form=auth())

# -------------------------------------------------------------------------------
@auth.requires_login()
def search():
    return dict()

# -------------------------------------------------------------------------------
@auth.requires_login()
def mark_friend():
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

    if len(request.args) == 0:
        active = "1"
    else:
        active = request.args[0]

    custom_friends = db(db.custom_friend.user_id == session.user_id).select(db.custom_friend.id)

    cusfriends = []
    for f in custom_friends:
        cusfriends.append(f.id)

    # Get the friends of logged in user
    query = db.friends.user_id == session.user_id
    friends = db(query).select(db.friends.friends_list).first()
    friends = tuple(eval(friends.friends_list))

    query = db.submission.user_id.belongs(friends)
    query |= db.submission.custom_user_id.belongs(cusfriends)
    count = db(query).count()
    count = count / 100 + 1

    if request.extension == "json":
        return dict(count=count)

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
