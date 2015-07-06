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

    for i in submissions[handle]:
        for j in submissions[handle][i]:
            submission = submissions[handle][i][j]
            if submission == {}:
                continue

            tr = TR()
            tr.append(TD(A(handle, _href=handle_url)))
            tr.append(TD(str(datetime.fromtimestamp(mktime(submission["time"])))))
            tr.append((TD(A(submission["problem_name"],
                            _href=str(submission["problem_link"])))))
            tr.append(TD(submission["status"]))
            tr.append(TD(submission["points"]))
            tr.append(TD(submission["language"]))
            table.append(tr)

    return table

def codechef():

    handle = "tryingtocode"
    P = profile.Profile(handle)
    submissions = P.codechef()
    handle_url = "https://www.codechef.com/users/" + handle
    table = user_submissions_table(submissions, handle, handle_url)
    return dict(handle=handle,
                table=table)

def codeforces():
    handle = "raj454raj"
    P = profile.Profile("", handle)
    submissions = P.codeforces()
    handle_url = "https://www.codeforces.com/profile/" + handle
    table = user_submissions_table(submissions, handle, handle_url)
    return dict(table=table,
                handle=handle)

def spoj():
    handle = "raj454raj"
    P = profile.Profile("", "", handle)
    submissions = P.spoj()
    handle_url = "http://www.spoj.com/users/" + handle
    table = user_submissions_table(submissions, handle, handle_url)
    return dict(table=table, handle=handle)
