"""
    Copyright (c) 2015-2016 Raj Patel(raj454raj@gmail.com), StopStalk

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

import re
import datetime
from operator import itemgetter
import utilities

# ----------------------------------------------------------------------------
def pie_chart_helper():
    """
        Helper function for populating pie chart with different
        submission status of a problem
    """

    problem_link = request.post_vars["plink"]
    stable = db.submission
    count = stable.id.count()
    query = (stable.problem_link == problem_link)

    # Show stats only for friends and logged-in user
    if session.auth:
        friends, cusfriends = utilities.get_friends(session.user_id)
        # The Original IDs of duplicate custom_friends
        custom_friends = []
        for cus_id in cusfriends:
            if cus_id[1] == None:
                custom_friends.append(cus_id[0])
            else:
                custom_friends.append(cus_id[1])

        query &= (stable.user_id.belongs(friends)) | \
                 (stable.custom_user_id.belongs(custom_friends)) | \
                 (stable.user_id == session.user_id)

    row = db(query).select(stable.status,
                           count,
                           groupby=stable.status)
    return dict(row=row)

# ----------------------------------------------------------------------------
def urltosite(url):
    """
        Helper function to extract site from url
    """

    # Note: try/except is not added because this function is not to
    #       be called for invalid problem urls
    site = re.search("www.*com", url).group()

    # Remove www. and .com from the url to get the site
    site = site[4:-4]

    return site

# ----------------------------------------------------------------------------
def index():
    """
        The main problem page
    """

    if request.vars.has_key("pname") == False or \
       request.vars.has_key("plink") == False:

        # Disables direct entering of a URL
        session.flash = "Please click on a Problem Link"
        redirect(URL("default", "index"))

    stable = db.submission
    ptable = db.problem_tags
    problem_name = request.vars["pname"]
    problem_link = request.vars["plink"]

    query = (stable.problem_link == problem_link)

    cusfriends = []
    # If a user is logged-in then show his/her friends' submissions
    if session.auth:
        friends, cusfriends = utilities.get_friends(session.user_id)
        # The Original IDs of duplicate custom_friends
        custom_friends = []
        for cus_id in cusfriends:
            if cus_id[1] == None:
                custom_friends.append(cus_id[0])
            else:
                custom_friends.append(cus_id[1])

        query &= (stable.user_id.belongs(friends)) | \
                 (stable.custom_user_id.belongs(custom_friends)) | \
                 (stable.user_id == session.user_id)

    submissions = db(query).select(orderby=~stable.time_stamp)

    try:
        query = (ptable.problem_link == problem_link)
        all_tags = db(query).select(ptable.tags).first()
        if all_tags:
            all_tags = eval(all_tags["tags"])
        else:
            all_tags = []
        if all_tags != [] and all_tags != ['-']:
            tags = DIV(_class="center")
            for tag in all_tags:
                tags.append(DIV(A(tag,
                                  _href=URL("problems",
                                            "tag",
                                            vars={"q": tag, "page": 1}),
                                  _style="color: white;",
                                  _target="_blank"),
                                _class="chip"))
                tags.append(" ")
        else:
            tags = DIV("No tags available")
    except AttributeError:
        tags = DIV("No tags available")

    problem_details = TABLE(_style="font-size: 140%;")
    tbody = TBODY()
    tbody.append(TR(TD(),
                    TD(STRONG("Problem Name:")),
                    TD(problem_name,
                       _id="problem_name"),
                    TD(_id="chart_div",
                       _style="width: 50%; height: 30%;",
                       _rowspan="4")))
    tbody.append(TR(TD(),
                    TD(STRONG("Site:")),
                    TD(urltosite(problem_link).capitalize())))
    tbody.append(TR(TD(),
                    TD(STRONG("Problem Link:")),
                    TD(A(I(_class="fa fa-link"), " Link",
                         _href=problem_link,
                         _target="_blank"))))
    tbody.append(TR(TD(),
                    TD(STRONG("Tags:")),
                    TD(tags)))
    problem_details.append(tbody)

    if len(submissions) == 0:
        table = DIV(H5("No submissions from your friends for this problem"),
                    _class="center")
    else:
        table = utilities.render_table(submissions, cusfriends)
        table = TAG[""](H4("Recent Submissions"),
                        table)

    return dict(problem_details=problem_details,
                problem_name=problem_name,
                problem_link=problem_link,
                table=table)

# ----------------------------------------------------------------------------
def tag():
    """
        Tag search page
    """

    table = TABLE(_class="striped centered")
    thead = THEAD(TR(TH("Problem Name"),
                     TH("Problem URL"),
                     TH("Site"),
                     TH("Tags")))
    table.append(thead)

    # If URL does not have vars containing q
    # then remain at the search page and return
    # an empty table
    if request.vars.has_key("q") is False:
        return dict(table=table)

    q = request.vars["q"]
    try:
        curr_page = int(request.vars["page"])
    except:
        curr_page = 1
    PER_PAGE = current.PER_PAGE

    # Enables multiple space seperated tag search
    q = q.split(" ")
    stable = db.submission
    ptable = db.problem_tags
    atable = db.auth_user
    cftable = db.custom_friend
    ftable = db.friends

    query = None
    for tag in q:
        if query is not None:
            # Decision to make & or |
            # & => Search for problem containing all these tags
            # | => Search for problem containing one of the tags
            query &= ptable.tags.contains(tag)
        else:
            query = ptable.tags.contains(tag)

    total_problems = db(query).count()
    total_pages = total_problems / PER_PAGE
    if total_problems % PER_PAGE != 0:
        total_pages = total_problems / PER_PAGE + 1

    if request.extension == "json":
        return dict(total_pages=total_pages)

    all_problems = db(query).select(ptable.problem_name,
                                    ptable.problem_link,
                                    ptable.tags,
                                    distinct=True,
                                    limitby=((curr_page - 1) * PER_PAGE,
                                             curr_page * PER_PAGE))

    tbody = TBODY()
    for problem in all_problems:

        tr = TR()

        tr.append(TD(A(problem["problem_name"],
                       _href=URL("problems",
                                 "index",
                                 vars={"pname": problem["problem_name"],
                                       "plink": problem["problem_link"]}),
                       _target="_blank")))
        tr.append(TD(A(I(_class="fa fa-link"),
                       _href=problem["problem_link"],
                       _target="_blank")))
        tr.append(TD(urltosite(problem["problem_link"]).capitalize()))
        all_tags = eval(problem["tags"])
        td = TD()
        for tag in all_tags:
            td.append(DIV(A(tag,
                            _href=URL("problems",
                                      "tag",
                                      vars={"q": tag, "page": 1}),
                            _style="color: white;",
                            _target="_blank"),
                          _class="chip"))
            td.append(" ")
        tr.append(td)
        tbody.append(tr)

    table.append(tbody)
    return dict(table=table)

# ----------------------------------------------------------------------------
def _render_trending(caption, rows, flag):
    """
        Create trending table from the rows
    """

    # Sort the rows according to the
    # number of users who solved the
    # problem in last PAST_DAYS
    rows = sorted(rows, key=lambda k: k["unique"], reverse=True)
    rows = rows[:current.PROBLEMS_PER_PAGE]
    problems = []
    for problem in rows:
        submission = problem["submission"]
        problems.append([submission["problem_name"],
                         submission["problem_link"],
                         problem["_extra"]["COUNT(submission.id)"],
                         problem["unique"]])

    problems = sorted(problems, key=itemgetter(3), reverse=True)

    table = TABLE(_class="striped centered")
    thead = THEAD(TR(TH("Problem"),
                     TH("Recent Submissions"),
                     TH(flag)))
    table.append(thead)
    tbody = TBODY()

    for problem in problems:
        tr = TR()
        tr.append(TD(A(problem[0],
                       _href=URL("problems", "index",
                                 vars={"pname": problem[0],
                                       "plink": problem[1]}),
                       _target="_blank")))
        tr.append(TD(problem[2]))
        tr.append(TD(problem[3]))
        tbody.append(tr)

    table.append(tbody)
    table = DIV(H4(caption, _class="center"), table)

    return table

# ----------------------------------------------------------------------------
def _get_total_users(trending_problems,
                     friends,
                     cusfriends,
                     start_date,
                     end_date):

    if friends == ():
        friends = ["-1"]
    if cusfriends == ():
        cusfriends = ["-1"]

    for problem in trending_problems:
        sql = """
                 SELECT COUNT(id)
                 FROM `submission`
                 WHERE ((problem_link = '%s')
                   AND ((user_id IN (%s))
                     OR (custom_user_id IN (%s)))
                   AND  ((time_stamp >= '%s')
                     AND (time_stamp <= '%s')))
                 GROUP BY user_id, custom_user_id
              """ % (problem["submission"]["problem_link"],
                     ", ".join(friends),
                     ", ".join(cusfriends),
                     start_date,
                     end_date)

        res = db.executesql(sql)
        problem["unique"] = len(res)

    return trending_problems

# ----------------------------------------------------------------------------
def trending():
    """
        Show trending problems globally and among friends
        @ToDo: Needs lot of comments explaining the code
    """

    stable = db.submission
    atable = db.auth_user
    cftable = db.custom_friend

    today = datetime.datetime.today()
    # Consider submissions only after PAST_DAYS(customisable)
    # for trending problems
    start_date = str(today - datetime.timedelta(days=current.PAST_DAYS))
    end_date = str(today)

    count = stable.id.count()

    if session.user_id:
        friends, cusfriends = utilities.get_friends(session.user_id)

        # The Original IDs of duplicate custom_friends
        custom_friends = []
        for cus_id in cusfriends:
            if cus_id[1] == None:
                custom_friends.append(cus_id[0])
            else:
                custom_friends.append(cus_id[1])

        first_query = (stable.user_id.belongs(friends))
        first_query |= (stable.custom_user_id.belongs(custom_friends))
        query = (stable.time_stamp >= start_date)
        query &= (stable.time_stamp <= end_date)
        query = first_query & query

        friend_trending = db(query).select(stable.problem_name,
                                           stable.problem_link,
                                           count,
                                           orderby=~count,
                                           groupby=stable.problem_link)

        friends = [str(x) for x in friends]
        custom_friends = [str(x) for x in custom_friends]
        friend_trending = _get_total_users(friend_trending.as_list(),
                                           friends,
                                           custom_friends,
                                           start_date,
                                           end_date)
        friend_table = _render_trending("Trending among friends",
                                        friend_trending,
                                        "Friends")

    friends = db(atable).select(atable.id)
    friends = [str(x["id"]) for x in friends.as_list()]
    cusfriends = db(cftable).select(cftable.id)
    cusfriends = [str(x["id"]) for x in cusfriends.as_list()]

    query = (stable.time_stamp >= start_date)
    query &= (stable.time_stamp <= end_date)
    global_trending = db(query).select(stable.problem_name,
                                       stable.problem_link,
                                       count,
                                       orderby=~count,
                                       groupby=stable.problem_link)
    global_trending = _get_total_users(global_trending.as_list(),
                                       friends,
                                       cusfriends,
                                       start_date,
                                       end_date)
    global_table = _render_trending("Trending Globally",
                                    global_trending,
                                    "Users")

    if session.user_id:
        div = DIV(_class="row col s12")
        div.append(DIV(friend_table, _class="col s6"))
        div.append(DIV(global_table, _class="col s6"))
    else:
        div = DIV(global_table, _class="center")

    return dict(div=div)

# END =========================================================================
