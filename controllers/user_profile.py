#profile = local_import("profile")
import profilesites as profile
from datetime import datetime
from time import mktime

# Return submissions as a table
def user_submissions_table(submissions, handle, handle_url):
    table = TABLE(_class="table")
    table.append(TR(TH("Handle"),
                    TH("Time"),
                    TH("Problem"),
                    TH("Status"),
                    TH("Points"),
                    TH("Language")))

    for i in sorted(submissions[handle].iterkeys()):
        for j in sorted(submissions[handle][i].iterkeys()):
            submission = submissions[handle][i][j]
            # submission = ["time", "problem_link", "problem_name", "status", "points", "language"]
            if submission == []:
                continue

            tr = TR()
            tr.append(TD(A(handle, _href=handle_url)))
            tr.append(TD(str(submission[0])))
            tr.append((TD(A(submission[2],
                            _href=str(submission[1])))))
            tr.append(TD(submission[3]))
            tr.append(TD(submission[4]))
            tr.append(TD(submission[5]))
            table.append(tr)

    return table

def codechef():

    handle = "raj_patel"
    P = profile.Profile(codechef_handle=handle)
    submissions = P.codechef()
    handle_url = "https://www.codechef.com/users/" + handle
    table = user_submissions_table(submissions, handle, handle_url)
    return dict(handle=handle,
                table=table)

def codeforces():
    handle = "raj454raj"
    P = profile.Profile(codeforces_handle=handle)
    submissions = P.codeforces()
    handle_url = "https://www.codeforces.com/profile/" + handle
    table = user_submissions_table(submissions, handle, handle_url)
    return dict(table=table,
                handle=handle)

def spoj():
    handle = "raj454raj"
    P = profile.Profile(spoj_handle=handle)
    submissions = P.spoj()
    handle_url = "http://www.spoj.com/users/" + handle
    table = user_submissions_table(submissions, handle, handle_url)
    return dict(table=table, handle=handle)
