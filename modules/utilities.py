from gluon import *

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
        tr.append(TD(submission.user_id.first_name + " " + submission.user_id.last_name))
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


