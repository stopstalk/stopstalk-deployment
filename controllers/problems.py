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

import datetime
import utilities

# ----------------------------------------------------------------------------
def pie_chart_helper():
    """
        Helper function for populating pie chart with different
        submission status of a problem
    """

    problem_link = request.post_vars["plink"]
    global_submissions = False
    if request.post_vars["global"] == "True":
        global_submissions = True

    stable = db.submission
    count = stable.id.count()
    query = (stable.problem_link == problem_link)

    # Show stats only for friends and logged-in user
    if global_submissions is False:
        if session.user_id:
            friends, cusfriends = utilities.get_friends(session.user_id)
            # The Original IDs of duplicate custom_friends
            custom_friends = []
            for cus_id in cusfriends:
                if cus_id[1] is None:
                    custom_friends.append(cus_id[0])
                else:
                    custom_friends.append(cus_id[1])

            query &= (stable.user_id.belongs(friends)) | \
                     (stable.custom_user_id.belongs(custom_friends)) | \
                     (stable.user_id == session.user_id)
        else:
            query &= (1 == 0)

    row = db(query).select(stable.status,
                           count,
                           groupby=stable.status)
    return dict(row=row)

# ----------------------------------------------------------------------------
def index():
    """
        The main problem page
    """

    if request.vars.has_key("pname") is False or \
       request.vars.has_key("plink") is False:

        # Disables direct entering of a URL
        session.flash = "Please click on a Problem Link"
        redirect(URL("default", "index"))

    global_submissions = False
    if request.vars.has_key("global"):
        if request.vars["global"] == "True":
            global_submissions = True

    stable = db.submission
    ptable = db.problem_tags
    petable = db.problem_editorial

    problem_name = request.vars["pname"]
    problem_link = request.vars["plink"]

    query = (stable.problem_link == problem_link)
    cusfriends = []

    if global_submissions is False:
        if auth.is_logged_in():
            friends, cusfriends = utilities.get_friends(session.user_id)
            # The Original IDs of duplicate custom_friends
            custom_friends = []
            for cus_id in cusfriends:
                if cus_id[1] is None:
                    custom_friends.append(cus_id[0])
                else:
                    custom_friends.append(cus_id[1])

            query &= (stable.user_id.belongs(friends)) | \
                     (stable.custom_user_id.belongs(custom_friends)) | \
                     (stable.user_id == session.user_id)
        else:
            session.flash = "Login to view Friends' Submissions"
            new_vars = request.vars
            new_vars["global"] = True
            redirect(URL("problems", "index",
                         vars=new_vars))

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

    site = utilities.urltosite(problem_link).capitalize()
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
                    TD(site)))

    links = DIV(DIV(A(I(_class="fa fa-link"), " Problem",
                      _href=problem_link,
                      _style="color: black;",
                      _target="blank"),
                    _class="chip lime accent-3"),
                _class="center")

    row = db(petable.problem_link == problem_link).select().first()
    if row and row.editorial_link:
        links.append(" ")
        links.append(DIV(A(I(_class="fa fa-book"), " Editorial",
                           _href=row.editorial_link,
                           _style="color: white;",
                           _target="_blank"),
                         _class="chip deep-purple darken-1"))
    tbody.append(TR(TD(),
                    TD(STRONG("Links:")),
                    links))
    tbody.append(TR(TD(),
                    TD(STRONG("Tags:")),
                    TD(tags)))
    problem_details.append(tbody)

    table = utilities.render_table(submissions, cusfriends)
    switch = DIV(LABEL(H6("Friends' Submissions",
                          INPUT(_type="checkbox", _id="submission-switch"),
                          SPAN(_class="lever pink accent-3"),
                          "Global Submissions")),
                 _class="switch")
    div = TAG[""](H4("Recent Submissions"), switch, table)

    return dict(site=site,
                problem_details=problem_details,
                problem_name=problem_name,
                problem_link=problem_link,
                global_submissions=global_submissions,
                div=div)

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
    ptable = db.problem_tags

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

        if problem["problem_link"] in current.solved_problems:
            link_class = "solved-problem"
        elif problem["problem_link"] in current.unsolved_problems:
            link_class = "unsolved-problem"
        else:
            link_class = "unattempted-problem"

        link_title = (" ".join(link_class.split("-"))).capitalize()

        tr.append(TD(A(problem["problem_name"],
                       _href=URL("problems",
                                 "index",
                                 vars={"pname": problem["problem_name"],
                                       "plink": problem["problem_link"]}),
                       _class=link_class,
                       _title=link_title,
                       _target="_blank")))
        tr.append(TD(A(I(_class="fa fa-link"),
                       _href=problem["problem_link"],
                       _target="_blank")))
        tr.append(TD(utilities.urltosite(problem["problem_link"]).capitalize()))
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
def _render_trending(caption, problems, flag):
    """
        Create trending table from the rows
    """

    table = TABLE(_class="striped centered")
    thead = THEAD(TR(TH("Problem"),
                     TH("Recent Submissions"),
                     TH(flag)))
    table.append(thead)
    tbody = TBODY()

    for problem in problems:
        tr = TR()

        if problem[0] in current.solved_problems:
            link_class = "solved-problem"
        elif problem[0] in current.unsolved_problems:
            link_class = "unsolved-problem"
        else:
            link_class = "unattempted-problem"

        link_title = (" ".join(link_class.split("-"))).capitalize()

        tr.append(TD(A(problem[1]["name"],
                       _href=URL("problems", "index",
                                 vars={"pname": problem[1]["name"],
                                       "plink": problem[0]}),
                       _class=link_class,
                       _title=link_title,
                       _target="_blank")))
        tr.append(TD(problem[1]["total_submissions"]))
        tr.append(TD(len(problem[1]["users"]) + \
                     len(problem[1]["custom_users"])))
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

    if friends == []:
        friends = ["-1"]
    if cusfriends == []:
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

    today = datetime.datetime.today()
    # Consider submissions only after PAST_DAYS(customizable)
    # for trending problems
    start_date = str(today - datetime.timedelta(days=current.PAST_DAYS))
    query = (stable.time_stamp >= start_date)
    last_submissions = db(query).select(stable.problem_name,
                                        stable.problem_link,
                                        stable.user_id,
                                        stable.custom_user_id)

    if auth.is_logged_in():
        friends, cusfriends = utilities.get_friends(session.user_id)

        # The Original IDs of duplicate custom_friends
        custom_friends = []
        for cus_id in cusfriends:
            if cus_id[1] is None:
                custom_friends.append(cus_id[0])
            else:
                custom_friends.append(cus_id[1])

    problems_dict = {}
    friends_problems_dict = {}
    for submission in last_submissions:
        plink = submission.problem_link
        pname = submission.problem_name
        uid = submission.user_id
        cid = submission.custom_user_id

        # @ToDo: Improve this code
        if problems_dict.has_key(plink):
            problems_dict[plink]["total_submissions"] += 1
        else:
            problems_dict[plink] = {"name": pname,
                                    "total_submissions": 1,
                                    "users": set([]),
                                    "custom_users": set([])}

        if auth.is_logged_in() and \
           ((uid and uid in friends) or \
            (cid and cid in custom_friends)):

            if friends_problems_dict.has_key(plink):
                friends_problems_dict[plink]["total_submissions"] += 1
            else:
                friends_problems_dict[plink] = {"name": pname,
                                                "total_submissions": 1,
                                                "users": set([]),
                                                "custom_users": set([])}
            if uid:
                friends_problems_dict[plink]["users"].add(uid)
            else:
                friends_problems_dict[plink]["custom_users"].add(cid)

        if uid:
            problems_dict[plink]["users"].add(uid)
        else:
            problems_dict[plink]["custom_users"].add(cid)

    # Sort the rows according to the number of users
    # who solved the problem in last PAST_DAYS
    custom_compare = lambda x: (len(x[1]["users"]) + \
                                len(x[1]["custom_users"]),
                                x[1]["total_submissions"])

    global_trending = sorted(problems_dict.items(),
                             key=custom_compare,
                             reverse=True)

    global_table = _render_trending("Trending Globally",
                                    global_trending[:current.PROBLEMS_PER_PAGE],
                                    "Users")
    if auth.is_logged_in():
        friends_trending = sorted(friends_problems_dict.items(),
                                  key=custom_compare,
                                  reverse=True)

        friend_table = _render_trending("Trending among friends",
                                        friends_trending[:current.PROBLEMS_PER_PAGE],
                                        "Friends")

        div = DIV(DIV(friend_table, _class="col s6"),
                  DIV(global_table, _class="col s6"),
                  _class="row col s12")
    else:
        div = DIV(global_table, _class="center")

    return dict(div=div)

# ==============================================================================
