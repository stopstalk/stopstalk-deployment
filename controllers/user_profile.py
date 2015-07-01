profile = local_import("profile")
from datetime import datetime
from time import mktime

def codechef():

    handle = "raj_patel"
    P = profile.Profile(handle)
    submissions = P.codechef()
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
            tr = TR()
            tr.append(TD(handle))
            tr.append(TD(str(datetime.fromtimestamp(mktime(submission["time"])))))
            tr.append((TD(A(submission["problem_name"],
                            _href=str(submission["problem_link"])))))
            tr.append(TD(submission["status"]))
            tr.append(TD(submission["points"]))
            tr.append(TD(submission["language"]))
            table.append(tr)

    return dict(handle=handle,
                table=table)

def codeforces():
    handle = "pranjalr34"
    P = profile.Profile("", handle)
    submissions = P.codeforces()
    
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
            tr.append(TD(handle))
            tr.append(TD(str(datetime.fromtimestamp(mktime(submission["time"])))))
            tr.append((TD(A(submission["problem_name"],
                            _href=str(submission["problem_link"])))))
            tr.append(TD(submission["status"]))
            tr.append(TD(submission["points"]))
            tr.append(TD(submission["language"]))
            table.append(tr)
    return dict(table=table,
                handle=handle)

def spoj():
    handle = "raj454raj"
    P = profile.Profile("", "", handle)
    submissions = P.spoj()

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
            tr.append(TD(handle))
            tr.append(TD(str(datetime.fromtimestamp(mktime(submission["time"])))))
            tr.append((TD(A(submission["problem_name"],
                            _href=str(submission["problem_link"])))))
            tr.append(TD(submission["status"]))
            tr.append(TD(submission["points"]))
            tr.append(TD(submission["language"]))
            table.append(tr)

    return dict(table=table, handle=handle)
