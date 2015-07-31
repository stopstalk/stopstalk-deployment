from gluon import *
import time
import profilesites as profile
from datetime import datetime, date

PROXY = {"http": "http://proxy.iiit.ac.in:8080/",
         "https": "https://proxy.iiit.ac.in:8080/"}

# -------------------------------------------------------------------------------
def _debug(first_name, last_name, site, custom=False):
    name = first_name + " " + last_name
    s = "Retrieving " + site + " submissions for "
    if custom:
        s += "CUSTOM USER "
    s += name
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
            tr.append(TD(A(submission.user_id.first_name + " " + submission.user_id.last_name,
                           _href=URL("user", "profile", args=[submission.stopstalk_handle]))))
        else:
            tr.append(TD(A(submission.custom_user_id.first_name + " " + submission.custom_user_id.last_name,
                           _href=URL("user", "profile", args=[submission.stopstalk_handle]))))
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
    count = 0
    for i in sorted(submissions[handle].iterkeys()):
        for j in sorted(submissions[handle][i].iterkeys()):
            submission = submissions[handle][i][j]
            if len(submission) == 6:
                count += 1
                args = dict(stopstalk_handle=stopstalk_handle,
                            site_handle=handle,
                            site=site,
                            time_stamp=submission[0],
                            problem_name=submission[2],
                            problem_link=submission[1],
                            lang=submission[5],
                            status=submission[3],
                            points=submission[4])

                if custom is False:
                    args["user_id"] = user_id
                else:
                    args["custom_user_id"] = user_id

                db.submission.insert(**args)

    print "\t --> Added %s submissions to the database" % (count)

# -------------------------------------------------------------------------------
def retrieve_submissions(reg_user, custom=False):
    """
        Retrieve submissions that are not already in the database
    """

    db = current.db
    stable = db.submission

    # Start retrieving from this date if user registered the first time
    initial_date = "2013-01-01 00:00:00"
    if custom:
        query = db.custom_friend.id == reg_user
        row = db(query).select().first()
        table = db.custom_friend
    else:
        query = (db.auth_user.id == reg_user)
        row = db(query).select().first()
        table = db.auth_user

    last_retrieved = db(query).select(table.last_retrieved).first()

    if last_retrieved:
        last_retrieved = str(last_retrieved.last_retrieved)
    else:
        last_retrieved = initial_date

    last_retrieved = time.strptime(str(last_retrieved), "%Y-%m-%d %H:%M:%S")

    # Update the last retrieved of the user
    today = time.strftime("%Y-%m-%d %H:%M:%S")
    db(query).update(last_retrieved=datetime.now())

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
