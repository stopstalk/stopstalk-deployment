"""
    Copyright (c) 2015-2020 Raj Patel(raj454raj@gmail.com), StopStalk

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in
    all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
    THE SOFTWARE.
"""

from utilities import *

# ----------------------------------------------------------------------------
def render_trending_table(caption, problems, column_name, user_id):
    """
        Create trending table from the rows
    """
    T = current.T

    table = TABLE(_class="bordered centered trendings-html-table")
    thead = THEAD(TR(TH(T("Problem")),
                     TH(T("Recent Submissions")),
                     TH(column_name)))
    table.append(thead)
    tbody = TBODY()

    for problem in problems:
        tr = TR()
        link_class, link_title = get_link_class(problem[0], user_id)

        tr.append(TD(problem_widget(problem[1]["name"],
                                    problem[1]["link"],
                                    link_class,
                                    link_title,
                                    problem[0]),
                     _class="left-align-problem"))
        tr.append(TD(problem[1]["total_submissions"]))
        tr.append(TD(len(problem[1]["users"]) + \
                     len(problem[1]["custom_users"])))
        tbody.append(tr)

    table.append(tbody)
    if caption is not None:
        table = DIV(H5(caption, _class="center"), HR(), table)

    return table

# ----------------------------------------------------------------------------
def get_trending_problem_list(submissions_list):
    # Sort the rows according to the number of users
    # who solved the problem in last PAST_DAYS
    custom_compare = lambda x: (len(x[1]["users"]) + \
                                len(x[1]["custom_users"]),
                                x[1]["total_submissions"])

    problems_dict = {}

    # Temporary cache for avoiding spam on redis for trending page
    cache_of_cache = {}
    for submission in submissions_list:
        if len(cache_of_cache) == 200:
            cache_of_cache = {}
        if submission.problem_id in cache_of_cache:
            problem_details = cache_of_cache[submission.problem_id]
        else:
            problem_details = get_problem_details(submission.problem_id)
            cache_of_cache[submission.problem_id] = problem_details
        plink = problem_details["link"]
        pname = problem_details["name"]
        uid = submission.user_id
        cid = submission.custom_user_id
        problem_id = submission.problem_id

        if problem_id not in problems_dict:
            problems_dict[problem_id] = {"name": pname,
                                         "total_submissions": 0,
                                         "users": set([]),
                                         "custom_users": set([]),
                                         "link": plink}

        pdict = problems_dict[problem_id]
        pdict["total_submissions"] += 1
        if uid:
            pdict["users"].add(uid)
        else:
            pdict["custom_users"].add(cid)

    trending_problems = sorted(problems_dict.items(),
                               key=custom_compare,
                               reverse=True)

    return trending_problems[:current.PROBLEMS_PER_PAGE]

# ----------------------------------------------------------------------------
def draw_trending_table(trending_problems, table_type, user_id):
    T = current.T
    if table_type == "friends":
        table_header = T("Trending among friends")
        column_name = T("Friends")
    elif table_type == "global":
        table_header = T("Trending Globally")
        column_name = T("Users")
    else:
        table_header = None
        column_name = T("Users")

    if len(trending_problems) == 0:
        table = TABLE(_class="bordered centered")
        thead = THEAD(TR(TH(T("Problem"), _class="left-align-problem"),
                         TH(T("Recent Submissions")),
                         TH(column_name)))
        table.append(thead)
        table.append(TBODY(TR(TD("Not enough data to show", _colspan=3))))
        return table

    return render_trending_table(
        table_header,
        trending_problems,
        column_name,
        user_id
    )

# ----------------------------------------------------------------------------
def compute_trending_table(submissions_list, table_type, user_id=None):
    """
        Create trending table from the rows

        @params submission_list (Rows): Submissions to be considered
        @params table_type (String): friends / global
        @params user_id (Long): ID of signed in user else None
    """


    trending_problems = get_trending_problem_list(submissions_list)

    return draw_trending_table(trending_problems, table_type, user_id)

# ------------------------------------------------------------------------------
def get_last_submissions_for_trending(extra_query):
    db = current.db
    stable = db.submission

    today = datetime.datetime.today()
    start_date = str(today - datetime.timedelta(days=current.PAST_DAYS))

    query = (stable.time_stamp >= start_date) & extra_query

    last_submissions = db(query).select(stable.problem_id,
                                        stable.user_id,
                                        stable.custom_user_id,
                                        orderby=stable.user_id|stable.site|stable.time_stamp)

    return last_submissions
