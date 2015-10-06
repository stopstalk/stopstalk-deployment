from gluon import *
import time
import profilesites as profile
from datetime import datetime, date

RED = "\x1b[1;31m"
GREEN = "\x1b[1;32m"
YELLOW = "\x1b[1;33m"
BLUE = "\x1b[1;34m"
MAGENTA = "\x1b[1;35m"
CYAN = "\x1b[1;36m"
RESET_COLOR = "\x1b[0m"

# -----------------------------------------------------------------------------
def _debug(first_name, last_name, site, custom=False):
    """
        Advanced logging of submissions
    """

    name = first_name + " " + last_name
    s = "Retrieving " + CYAN + site + RESET_COLOR + " submissions for "
    if custom:
        s += "CUSTOM USER "
    s += BLUE + name + RESET_COLOR
    print s,

# -----------------------------------------------------------------------------
def get_link(site, handle):
    """
        Get the URL of site_handle
    """

    return current.SITES[site] + handle

# -----------------------------------------------------------------------------
def render_table(submissions):
    """
        Create the HTML table from submissions
    """

    status_dict = {"AC": "Accepted",
                   "WA": "Wrong Answer",
                   "TLE": "Time Limit Exceeded",
                   "MLE": "Memory Limit Exceeded",
                   "RE": "Runtime Error",
                   "CE": "Compile Error",
                   "SK": "Skipped",
                   "HCK": "Hacked",
                   "OTH": "Others",
                   }

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
        append = tr.append

        person_id = submission.custom_user_id
        if submission.user_id:
            person_id = submission.user_id

        append(TD(A(person_id.first_name + " " + person_id.last_name,
                    _href=URL("user", "profile",
                              args=[submission.stopstalk_handle]),
                    _target="_blank")))
        append(TD(submission.site))
        append(TD(A(submission.site_handle,
                    _href=get_link(submission.site,
                                   submission.site_handle),
                    _target="_blank")))
        append(TD(submission.time_stamp))
        append(TD(A(submission.problem_name,
                    _href=submission.problem_link,
                    _target="_blank")))
        append(TD(submission.lang))
        append(TD(IMG(_src=URL("static",
                               "images/" + submission.status + ".jpg"),
                      _title=status_dict[submission.status],
                      _style="height: 25px; width: 25px;")))
        append(TD(submission.points))
        table.append(tr)

    return table

# -----------------------------------------------------------------------------
def get_submissions(user_id,
                    handle,
                    stopstalk_handle,
                    submissions,
                    site,
                    custom=False):
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

    if count != 0:
        print RED + "[+%s] " % (count) + RESET_COLOR
    else:
        print "[0]"

# ----------------------------------------------------------------------------
def retrieve_submissions(reg_user, custom=False):
    """
        Retrieve submissions that are not already in the database
    """

    db = current.db
    stable = db.submission

    # Start retrieving from this date if user registered the first time
    initial_date = current.INITIAL_DATE
    time_conversion = "%Y-%m-%d %H:%M:%S"
    if custom:
        query = (db.custom_friend.id == reg_user)
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

    last_retrieved = time.strptime(str(last_retrieved), time_conversion)

    # Update the last retrieved of the user
    today = datetime.now()
    db(query).update(last_retrieved=today)

    for site in current.SITES:
        site_handle = row[site.lower() + "_handle"]
        if site_handle:
            _debug(row.first_name, row.last_name, site, custom)

            P = profile.Profile(site, site_handle)
            site_method = getattr(P, site.lower())
            submissions = site_method(last_retrieved)
            get_submissions(reg_user,
                            site_handle,
                            row.stopstalk_handle,
                            submissions,
                            site,
                            custom)
