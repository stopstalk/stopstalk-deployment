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
import utilities

# ----------------------------------------------------------------------------
def pie_chart_helper():
    """
        Helper function for populating pie chart with different
        submission status of a problem
    """

    problem_name = request.post_vars["pname"]
    stable = db.submission
    count = stable.id.count()
    query = (stable.problem_name == problem_name)
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

    # If a user is logged-in then show his/her friends' submissions
    if session.auth:
        friends, cusfriends = utilities.get_friends(session.user_id)
        query &= (stable.user_id.belongs(friends)) | \
                 (stable.custom_user_id.belongs(cusfriends)) | \
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
    table = utilities.render_table(submissions)

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
                     TH("Problem Page"),
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

    # If a user is logged in then only show problems that are solved by
    # his/her friends, custom friends and also himself/herself.
    if session.auth:
        friends, cusfriends = utilities.get_friends(session.user_id)
        query = (stable.user_id.belongs(friends))
        query |= (stable.user_id == session.user_id)
        query |= (stable.custom_user_id.belongs(cusfriends))

        # All the URLs of problems
        problem_links = db(query).select(stable.problem_link, distinct=True)
        problem_links = [x["problem_link"] for x in problem_links]

    query = None
    for tag in q:
        if query is not None:
            # Decision to make & or |
            # & => Search for problem containing all these tags
            # | => Search for problem containing one of the tags
            query &= ptable.tags.contains(tag)
        else:
            query = ptable.tags.contains(tag)

    if session.auth:
        query &= ptable.problem_link.belongs(problem_links)

    join_query = (stable.problem_link == ptable.problem_link)

    # @Todo: Need a cleanup here
    total_problems = db(query).select(stable.problem_link,
                                      ptable.tags,
                                      left=ptable.on(join_query),
                                      distinct=True)

    total_problems = len(total_problems)
    total_pages = total_problems / PER_PAGE
    if total_problems % PER_PAGE != 0:
        total_pages = total_problems / PER_PAGE + 1

    if request.extension == "json":
        return dict(total_pages=total_pages)

    all_problems = db(query).select(stable.problem_name,
                                    stable.problem_link,
                                    stable.site,
                                    ptable.tags,
                                    left=ptable.on(join_query),
                                    distinct=True,
                                    limitby=((curr_page - 1) * PER_PAGE,
                                             curr_page * PER_PAGE))

    tbody = TBODY()
    for problem in all_problems:

        submission = problem["submission"]
        problem_tag = problem["problem_tags"]
        tr = TR()

        tr.append(TD(A(submission["problem_name"],
                       _href=URL("problems",
                                 "index",
                                 vars={"pname": submission["problem_name"],
                                       "plink": submission["problem_link"]}),
                       _target="_blank")))
        tr.append(TD(A(I(_class="fa fa-link"),
                       _href=submission["problem_link"],
                       _target="_blank")))
        tr.append(TD(submission["site"]))
        all_tags = eval(problem_tag["tags"])
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
def _render_trending(caption, rows):
    """
        Create trending table from the rows
    """

    table = TABLE(_class="striped centered")
    thead = THEAD(TR(TH("Problem"), TH("Submissions")))
    table.append(thead)
    tbody = TBODY()
    for problem in rows:
        tr = TR()
        submission = problem["submission"]
        tr.append(TD(A(problem["submission"]["problem_name"],
                       _href=URL("problems", "index",
                                 vars={"pname": submission["problem_name"],
                                       "plink": submission["problem_link"]}),
                       _target="_blank")))
        tr.append(TD(problem["_extra"]["COUNT(submission.id)"]))
        tbody.append(tr)

    table.append(tbody)
    table = DIV(H4(caption, _class="center"), table)

    return table

# ----------------------------------------------------------------------------
def trending():
    """
        Show trending problems globally and among friends
    """

    stable = db.submission

    today = datetime.datetime.today()
    start_date = str(today - datetime.timedelta(days=current.PAST_DAYS))
    end_date = str(today)

    count = stable.id.count()
    PROBLEMS_PER_PAGE = current.PROBLEMS_PER_PAGE

    if session.user_id:
        friends, custom_friends = utilities.get_friends(session.user_id)

        query = (stable.user_id.belongs(friends))
        query |= (stable.custom_user_id.belongs(custom_friends))
        query &= (stable.time_stamp >= start_date)
        query &= (stable.time_stamp <= end_date)

        friend_trending = db(query).select(stable.problem_name,
                                           stable.problem_link,
                                           count,
                                           orderby=~count,
                                           groupby=stable.problem_link,
                                           limitby=(0, PROBLEMS_PER_PAGE))
        friend_table = _render_trending("Trending among friends",
                                        friend_trending)

    query = (stable.time_stamp >= start_date)
    query &= (stable.time_stamp <= end_date)
    global_trending = db(query).select(stable.problem_name,
                                       stable.problem_link,
                                       count,
                                       orderby=~count,
                                       groupby=stable.problem_link,
                                       limitby=(0, PROBLEMS_PER_PAGE))
    global_table = _render_trending("Trending Globally", global_trending)

    if session.user_id:
        div = DIV(_class="row col s12")
        div.append(DIV(friend_table, _class="col s6"))
        div.append(DIV(global_table, _class="col s6"))
    else:
        div = DIV(global_table, _class="center")

    return dict(div=div)

# END =========================================================================
