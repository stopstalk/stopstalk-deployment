from gluon import *
import time
import profilesites as profile
from datetime import datetime

# -------------------------------------------------------------------------------
def _debug(first_name, last_name, site, custom=False):
    name = first_name + " " + last_name
    s = "Retrieving " + site + " submissions for "
    if custom:
        s += "CUSTOM USER "
    s += name + " ..."
    print s

# -------------------------------------------------------------------------------
def get_link(site, handle):
    site_dict = {"CodeChef": "http://www.codechef.com/users/",
                 "CodeForces": "http://www.codeforces.com/profile/",
                 "Spoj": "http://www.spoj.com/users/"}
    return site_dict[site] + handle

# -------------------------------------------------------------------------------
def render_table(submissions):

    table = TABLE(_class="table")
    table.append(TR(TH("User Name"),
                    TH("Site"),
                    TH("Site Handle"),
                    TH("Time of submission"),
                    TH("Problem"),
                    TH("Language"),
                    TH("Status"),
                    TH("Points")))

    for submission in submissions:
        tr = TR()
        if submission.user_id:
            tr.append(TD(submission.user_id.first_name + " " + submission.user_id.last_name))
        else:
            tr.append(TD(submission.custom_user_id.first_name + " " + submission.custom_user_id.last_name))
        tr.append(TD(submission.site))
        tr.append(TD(A(submission.site_handle,
                       _href=get_link(submission.site,
                                      submission.site_handle))))
        tr.append(TD(submission.time_stamp))
        tr.append(TD(A(submission.problem_name,
                       _href=submission.problem_link)))
        tr.append(TD(submission.lang))
        tr.append(TD(submission.status))
        tr.append(TD(submission.points))
        table.append(tr)

    return table

# -------------------------------------------------------------------------------
def get_submissions(user_id, handle, stopstalk_handle, submissions, site, custom=False):
    """
        Get the submissions and populate the database
    """

    db = current.db
    for i in sorted(submissions[handle].iterkeys()):
        for j in sorted(submissions[handle][i].iterkeys()):
            submission = submissions[handle][i][j]
            if len(submission) == 6:
                if custom is False:
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
                else:
                    db.submission.insert(custom_user_id=user_id,
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
def retrieve_submissions(reg_user, custom=False):
    """
        Retrieve submissions that are not already in the database
    """

    db = current.db
    if custom:
        row = db(db.custom_friend.id == reg_user).select().first()
    else:
        row = db(db.auth_user.id == reg_user).select().first()

    # Start retrieving from this date if user registered the first time
    initial_date = "2013-01-01 00:00:00"
    if custom:
        last_retrieved = db(db.submission.custom_user_id == reg_user).select(orderby=~db.submission.time_stamp).first()
    else:
        last_retrieved = db(db.submission.user_id == reg_user).select(orderby=~db.submission.time_stamp).first()

    if last_retrieved:
        last_retrieved = last_retrieved.time_stamp
    else:
        last_retrieved = initial_date

    last_retrieved = time.strptime(str(last_retrieved), "%Y-%m-%d %H:%M:%S")

    # ToDo: Make this generalized and extensible if a site is added
    if row.codechef_handle:

        _debug(row.first_name, row.last_name, "CodeChef", custom)

        handle = row.codechef_handle
        P = profile.Profile(codechef_handle=handle)
        submissions = P.codechef(last_retrieved)
        get_submissions(reg_user,
                        handle,
                        row.stopstalk_handle,
                        submissions,
                        "CodeChef",
                        custom)

    if row.codeforces_handle:

        _debug(row.first_name, row.last_name, "CodeForces", custom)

        handle = row.codeforces_handle
        P = profile.Profile(codeforces_handle=handle)
        submissions = P.codeforces(last_retrieved)
        get_submissions(reg_user,
                        handle,
                        row.stopstalk_handle,
                        submissions,
                        "CodeForces",
                        custom)

    if row.spoj_handle:

        _debug(row.first_name, row.last_name, "Spoj", custom)

        handle = row.spoj_handle
        P = profile.Profile(spoj_handle=handle)
        submissions = P.spoj(last_retrieved)
        get_submissions(reg_user,
                        handle,
                        row.stopstalk_handle,
                        submissions,
                        "Spoj",
                        custom)
