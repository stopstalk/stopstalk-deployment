# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
#########################################################################


def index():
    """
    """
    if session["auth"]:
        session["handle"] = session["auth"]["user"]["stopstalk_handle"]
        session["user_id"] = session["auth"]["user"]["id"]
        redirect(URL("default", "submissions"))

    # Detect a registration has taken place
    row = db(db.auth_event.id > 0).select().last()
    desc = row.description
    if desc.__contains__("Registered"):
        reg_user = desc.split(" ")[1]
        r = db(db.friends.user_id == reg_user).select()
        
        # User has a `set` of friends' ids
        # If user does not exists then initialize it with empty set
        if len(r) == 0:
            db.friends.insert(user_id=int(reg_user), friends_list=str(set([])))

    response.flash = T("Please Login")
    return dict(message=T('Welcome to web2py!'))

def user():
    return dict(form=auth())

@auth.requires_login()
def submissions():
    return dict()

def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()
