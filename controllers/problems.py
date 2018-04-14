"""
    Copyright (c) 2015-2018 Raj Patel(raj454raj@gmail.com), StopStalk

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
    submission_type = "friends"

    if request.vars.has_key("submission_type"):
        if request.vars["submission_type"] == "global":
            submission_type = "global"
        elif request.vars["submission_type"] == "my":
            submission_type = "my"

    if auth.is_logged_in() is False:
        submission_type = "global"

    stable = db.submission
    count = stable.id.count()
    query = (stable.problem_link == problem_link)

    # Show stats only for friends and logged-in user
    if submission_type in ("my", "friends"):
        if auth.is_logged_in():
            if submission_type == "friends":
                friends, cusfriends = utilities.get_friends(session.user_id)
                # The Original IDs of duplicate custom_friends
                custom_friends = []
                for cus_id in cusfriends:
                    if cus_id[1] is None:
                        custom_friends.append(cus_id[0])
                    else:
                        custom_friends.append(cus_id[1])

                query &= (stable.user_id.belongs(friends)) | \
                         (stable.custom_user_id.belongs(custom_friends))
            else:
                query &= (stable.user_id == session.user_id)
        else:
            return dict(row=[])
    row = db(query).select(stable.status,
                           count,
                           groupby=stable.status)
    return dict(row=row)

# ----------------------------------------------------------------------------
@auth.requires_login()
def get_tag_values():
    ttable = db.tag
    all_tags = db(ttable).select(orderby=ttable.value)
    tags = []
    for tag in all_tags:
        tags.append({"value": tag.id, "text": tag.value})
    return dict(tags=tags)

# ----------------------------------------------------------------------------
@auth.requires_login()
def add_todo_problem():
    link = request.vars["link"]
    tltable = db.todo_list
    query = (tltable.problem_link == link) & \
            (tltable.user_id == session.user_id)
    row = db(query).select().first()
    if row:
        return T("Problem already in ToDo List")
    else:
        tltable.insert(problem_link=link, user_id=session.user_id)

    return T("Problem added to ToDo List")

# ----------------------------------------------------------------------------
@auth.requires_login()
def add_suggested_tags():

    sttable = db.suggested_tags
    ptable = db.problem
    ttable = db.tag

    plink = request.vars["plink"]
    pname = request.vars["pname"]
    tags = request.vars["tags"]

    today = datetime.datetime.now().strftime("%Y-%m-%d")
    problem = db(ptable.link == plink).select().first()
    if problem:
        problem_id = problem.id
    else:
        return T("Problem not found")

    # Delete previously added tags for the same problem by the user
    delete_query = (sttable.problem_id == problem_id) & \
                   (sttable.user_id == session.user_id)
    db(delete_query).delete()

    possible_tag_ids = db(ttable).select(ttable.id)
    possible_tag_ids = set([x.id for x in possible_tag_ids])

    if tags == "":
        return T("Tags updated successfully!")

    tag_ids = [int(x) for x in tags.split(",")]
    for tag_id in tag_ids:
        if tag_id in possible_tag_ids:
            sttable.insert(user_id=session.user_id,
                           problem_id=problem_id,
                           tag_id=tag_id)

    return T("Tags added successfully!")

# ----------------------------------------------------------------------------
@auth.requires_login()
def get_suggested_tags():

    empty_response = dict(user_tags=[], tag_counts=[])
    if request.extension != "json":
        return empty_response

    ptable = db.problem
    sttable = db.suggested_tags
    ttable = db.tag

    rows = db(ttable).select()
    all_tags = {}
    for row in rows:
        all_tags[row.id] = row.value

    plink = request.vars["plink"]
    problem = db(ptable.link == plink).select().first()
    if problem:
        problem_id = problem.id
    else:
        return empty_response
    tags_by_user = []
    query = (sttable.problem_id == problem_id) & \
            (sttable.user_id == session.user_id)
    rows = db(query).select(sttable.tag_id)

    def _represent_tag(tag_id):
        return {"value": tag_id, "text": all_tags[tag_id]}
    user_tags = []
    for row in rows:
        user_tags.append(_represent_tag(row.tag_id))

    cnt = sttable.id.count()
    query = (sttable.problem_id == problem_id)
    tags = db(query).select(sttable.tag_id,
                            cnt,
                            groupby=sttable.tag_id,
                            orderby=~cnt)
    tag_counts = []
    for row in tags:
        tag_counts.append([_represent_tag(row.suggested_tags.tag_id),
                           row["_extra"]["COUNT(suggested_tags.id)"]])

    return dict(user_tags=user_tags,
                tag_counts=tag_counts)

# ----------------------------------------------------------------------------
def index():
    """
        The main problem page
    """
    from json import dumps

    if request.vars.has_key("pname") is False or \
       request.vars.has_key("plink") is False:

        # Disables direct entering of a URL
        session.flash = T("Please click on a Problem Link")
        redirect(URL("default", "index"))

    submission_type = "friends"
    if request.vars.has_key("submission_type"):
        if request.vars["submission_type"] == "global":
            submission_type = "global"
        elif request.vars["submission_type"] == "my":
            submission_type = "my"

    if auth.is_logged_in() is False and submission_type != "global":
        response.flash = T("Login to view your/friends' submissions")
        submission_type = "global"

    stable = db.submission
    ptable = db.problem

    problem_name = request.vars["pname"]
    problem_link = request.vars["plink"]

    query = (stable.problem_link == problem_link)
    cusfriends = []

    if submission_type in ("my", "friends"):
        if auth.is_logged_in():
            if submission_type == "friends":
                friends, cusfriends = utilities.get_friends(session.user_id)
                # The Original IDs of duplicate custom_friends
                custom_friends = []
                for cus_id in cusfriends:
                    if cus_id[1] is None:
                        custom_friends.append(cus_id[0])
                    else:
                        custom_friends.append(cus_id[1])

                query &= (stable.user_id.belongs(friends)) | \
                         (stable.custom_user_id.belongs(custom_friends))
            else:
                query &= (stable.user_id == session.user_id)
        else:
            response.flash = T("Login to view your/friends' submissions")

    submissions = db(query).select(orderby=~stable.time_stamp)
    problem_record = db(ptable.link == problem_link).select().first()
    try:
        all_tags = problem_record.tags
        if all_tags:
            all_tags = eval(all_tags)
        else:
            all_tags = ["-"]
    except AttributeError:
        all_tags = ["-"]

    site = utilities.urltosite(problem_link).capitalize()
    problem_details = DIV(_class="row")
    details_table = TABLE(_style="font-size: 140%; float: left; width: 50%;")
    problem_class = ""

    link_class = utilities.get_link_class(problem_link, session.user_id)
    link_title = (" ".join(link_class.split("-"))).capitalize()

    tbody = TBODY()
    tbody.append(TR(TD(),
                    TD(STRONG(T("Problem Name") + ":")),
                    TD(utilities.problem_widget(problem_name,
                                                problem_link,
                                                link_class,
                                                link_title,
                                                anchor=False),
                       _id="problem_name")))
    tbody.append(TR(TD(),
                    TD(STRONG(T("Site") + ":")),
                    TD(site)))

    links = DIV(DIV(A(I(_class="fa fa-link"), " " + T("Problem"),
                      _href=problem_link,
                      _class="problem-page-site-link",
                      _style="color: black;",
                      _target="blank"),
                    _class="chip lime accent-3"))

    row = db(ptable.link == problem_link).select().first()
    if row:
        links.append(" ")
        links.append(DIV(A(I(_class="fa fa-book"), " " + T("Editorials"),
                           _href=URL("problems", "editorials", args=row.id),
                           _class="problem-page-editorials",
                           _style="color: white;",
                           _target="_blank"),
                         _class="chip deep-purple darken-1"))

    tbody.append(TR(TD(),
                    TD(STRONG(T("Links") + ":")),
                    links))

    suggest_tags_class = "disabled btn chip tooltipped suggest-tags-plus-logged-out"
    suggest_tags_data = {"position": "right",
                         "delay": "50",
                         "tooltip": T("Login to suggest tags")}
    suggest_tags_id = "disabled-suggest-tags"
    if auth.is_logged_in():
        suggest_tags_class = "green chip waves-light waves-effect tooltipped suggest-tags-plus modal-trigger"
        suggest_tags_data["target"] = "suggest-tags-modal"
        suggest_tags_data["tooltip"] = T("Suggest tags")
        suggest_tags_id = "suggest-trigger"

    tbody.append(TR(TD(),
                    TD(STRONG(T("Tags") + ":")),
                    TD(DIV(SPAN(A(I(_class="fa fa-tag"), " Show Tags",
                                 _id="show-tags",
                                 _class="chip orange darken-1",
                                 data={"tags": dumps(all_tags)}),
                                _id="tags-span"),
                           " ",
                           BUTTON(I(_class="fa fa-plus"),
                                  _style="color: white; margin-top: 7px;",
                                  _class=suggest_tags_class,
                                  _id=suggest_tags_id,
                                  data=suggest_tags_data)))))

    details_table.append(tbody)
    problem_details.append(details_table)
    problem_details.append(DIV(_style="width: 50%; margin-top: 3%",
                               _id="chart_div",
                               _class="right"))

    table = utilities.render_table(submissions, cusfriends, session.user_id)

    return dict(site=site,
                problem_details=problem_details,
                problem_name=problem_name,
                problem_link=problem_link,
                submission_type=submission_type,
                table=table)

# ----------------------------------------------------------------------------
def editorials():
    if len(request.args) < 1:
        redirect(URL("default", "index"))
    record = db.problem(int(request.args[0]))
    if record is None:
        redirect(URL("default", "index"))

    uetable = db.user_editorials
    atable = db.auth_user
    query = (uetable.problem_id == record.id)
    if auth.is_logged_in():
        # Show only accepted editorials not made by the logged-in user and
        # all the editorials submitted by the logged-in user
        query &= (((uetable.verification == "accepted") & \
                   (uetable.user_id != session.user_id)) | \
                  (uetable.user_id == session.user_id))
    else:
        query &= (uetable.verification == "accepted")
    user_editorials = db(query).select(orderby=~uetable.added_on)
    table = TABLE(_class="centered")
    thead = THEAD(TR(TH(T("Problem")),
                     TH(T("Editorial By")),
                     TH(T("Added on")),
                     TH(T("Votes")),
                     TH(T("Actions"))))
    color_mapping = {"accepted": "green",
                     "rejected": "red",
                     "pending": "blue"}

    tbody = TBODY()
    for editorial in user_editorials:
        user = atable(editorial.user_id)
        number_of_votes = len(editorial.votes.split(",")) if editorial.votes else 0
        tr = TR(TD(A(record.name,
                     _href=URL("problems",
                               "index",
                               vars={"pname": record.name,
                                     "plink": record.link},
                               extension=False))))
        if auth.is_logged_in() and user.id == session.user_id:
            tr.append(TD(A(user.first_name + " " + user.last_name,
                         _href=URL("user",
                                   "profile",
                                   args=user.stopstalk_handle)),
                         " ",
                         DIV(editorial.verification.capitalize(),
                             _class="verification-badge " + \
                                    color_mapping[editorial.verification])))
        else:
            tr.append(TD(A(user.first_name + " " + user.last_name,
                           _href=URL("user",
                                     "profile",
                                     args=user.stopstalk_handle))))

        tr.append(TD(editorial.added_on))
        vote_class = ""
        if auth.is_logged_in() and str(session.user_id) in set(editorial.votes.split(",")):
            vote_class = "red-text"
        tr.append(TD(DIV(SPAN(I(_class="fa fa-heart " + vote_class),
                              _class="love-editorial",
                              data={"id": editorial.id}),
                         " ",
                         DIV(number_of_votes,
                             _class="love-count",
                             _style="margin-left: 5px;"),
                         _style="display: inline-flex;")))

        actions_td = TD(A(I(_class="fa fa-eye fa-2x"),
                          _href=URL("problems",
                                    "read_editorial",
                                    args=editorial.id),
                          _class="btn btn-primary tooltipped",
                          _style="background-color: #13AA5F;",
                          data={"position": "bottom",
                                "delay": 40,
                                "tooltip": T("Read Editorial")}))
        if auth.is_logged_in() and \
           user.id == session.user_id and \
           editorial.verification != "accepted":
            actions_td.append(BUTTON(I(_class="fa fa-trash fa-2x"),
                                     _style="margin-left: 2%;",
                                     _class="red tooltipped delete-editorial",
                                     data={"position": "bottom",
                                           "delay": 40,
                                           "tooltip": T("Delete Editorial"),
                                           "id": editorial.id}))
        tr.append(actions_td)
        tbody.append(tr)

    table.append(thead)
    table.append(tbody)

    return dict(name=record.name,
                link=record.link,
                editorial_link=record.editorial_link,
                table=table,
                problem_id=record.id,
                site=utilities.urltosite(record.link))

# ----------------------------------------------------------------------------
@auth.requires_login()
def delete_editorial():
    if len(request.args) < 1:
        raise(HTTP(400, "Bad request"))
        return

    ue_record = db.user_editorials(int(request.args[0]))
    if ue_record is None or session.user_id != ue_record.user_id:
        raise(HTTP(400, "Bad request"))
        return

    if ue_record.verification == "accepted":
        return "ACCEPTED_EDITORIAL"

    ue_record.delete_record()

    # if current.environment == "production":
    #     client = utilities.get_boto3_client()
    #     # Don't delete s3 files for now
    #     client.delete_object(Bucket=current.s3_bucket,
    #                          Key=ue_record.s3_key)
    # else:
    #     import os
    #     os.remove(request.folder + "user_editorials/" + ue_record.s3_key)

    return "SUCCESS"

# ----------------------------------------------------------------------------
def read_editorial():
    if len(request.args) < 1:
        redirect(URL("default", "index"))

    uetable = db.user_editorials
    ptable = db.problem
    atable = db.auth_user
    ue_record = uetable(int(request.args[0]))

    # @ToDo: Refactor this later !
    if ue_record is None:
        session.flash = "Invalid editorial URL"
        redirect(URL("default", "index"))
    elif auth.is_logged_in() and session.user_id == 1:
        # Admin user
        pass
    elif auth.is_logged_in() and session.user_id != ue_record.user_id and ue_record.verification != "accepted":
        session.flash = "Invalid editorial URL"
        redirect(URL("default", "index"))
    elif auth.is_logged_in() == False and ue_record.verification != "accepted":
        session.flash = "Invalid editorial URL"
        redirect(URL("default", "index"))
    elif auth.is_logged_in() and session.user_id != ue_record.user_id and ue_record.verification != "accepted":
        session.flash = "Invalid editorial URL"
        redirect(URL("default", "index"))

    user = atable(ue_record.user_id)
    problem = ptable(ue_record.problem_id)
    editorials_dir = request.folder + "user_editorials/"
    s3_key = ue_record.s3_key
    filename = editorials_dir + s3_key

    def read_file():
        f = open(filename, "r")
        content = f.read()
        f.close()
        return content

    def download_from_s3():
        client = utilities.get_boto3_client()
        client.download_file(current.s3_bucket, s3_key, filename)

    if current.environment == "production":
        import os
        download_from_s3()
        content = read_file()
    else:
        content = read_file()

    return dict(problem_name=problem.name,
                problem_link=problem.link,
                stopstalk_handle=user.stopstalk_handle,
                content=content,
                all_editorials_link=URL("problems",
                                        "editorials",
                                        args=problem.id))

# ----------------------------------------------------------------------------
@auth.requires_login()
def submit_editorial():
    from uuid import uuid4
    problem_id = request.vars.get("problem_id", None)
    content = request.vars.get("content", None)
    editorials_dir = request.folder + "user_editorials/"
    if problem_id is None or content is None:
        raise HTTP(400, "Bad Request")
        return dict(error="Invalid request params")

    s3_key = "editorials/" + problem_id + "_" + str(session.user_id) + \
             "_" + str(uuid4()).split("-")[0] + ".txt"

    def create_editorial_file(filename):
        file_obj = open(filename, "w")
        file_obj.write(content)
        file_obj.close()

    def upload_to_s3():
        import os
        filename = editorials_dir + s3_key
        create_editorial_file(filename)
        client = utilities.get_boto3_client()
        try:
            client.upload_file(filename,
                               current.s3_bucket,
                               s3_key)
            # Delete the local file
            os.remove(filename)
        except:
            pass

    def upload_to_filesystem():
        # Used in case of development environments
        create_editorial_file(editorials_dir + s3_key)

    if current.environment == "production":
        upload_to_s3()
    else:
        upload_to_filesystem()
    new_editorial_id = db.user_editorials.insert(user_id=session.user_id,
                                                 problem_id=problem_id,
                                                 s3_key=s3_key,
                                                 votes="",
                                                 added_on=datetime.datetime.now(),
                                                 verification="pending")

    current.send_mail(to="raj454raj@gmail.com",
                      subject="New editorial by " + session.handle + " for " + problem_id,
                      message="""<html>
                                    %s<br/>
                                    <a href='%s'>Accept</a>
                                    <a href='%s'>Reject</a>
                                 </html>""" % (URL("problems",
                                                   "read_editorial",
                                                   args=new_editorial_id,
                                                   scheme=True,
                                                   host=True),
                                               URL("problems",
                                                   "admin_editorial_approval",
                                                   args=["accepted", new_editorial_id],
                                                   scheme=True,
                                                   host=True),
                                               URL("problems",
                                                   "admin_editorial_approval",
                                                   args=["rejected", new_editorial_id],
                                                   scheme=True,
                                                   host=True)),
                      mail_type="admin",
                      bulk=True)
    return dict()

# ----------------------------------------------------------------------------
@auth.requires_login()
def admin_editorial_approval():
    if session.user_id != 1 or len(request.args) < 2:
        raise(HTTP(401, "Why are you here ?"))
        return

    uetable = db.user_editorials
    uetable_record = uetable(request.args[1])
    user = db.auth_user(uetable_record.user_id)
    if request.args[0] == "accepted":
        current.send_mail(to=user.email,
                          subject="Your editorial on StopStalk is Published",
                          message="""
<html>
Hello %s,<br/><br/>

Your <a href="%s">editorial</a> on StopStalk is <b>Approved</b>. Thank you for your valuable contribution to the community.<br/>
Please share your editorial link on our Official <a href="https://www.facebook.com/groups/stopstalk/">Facebook Group</a> to help other Competitive Programmers.
<br/><br/>

Cheers,<br/>
Team StopStalk

</html>
""" % (user.stopstalk_handle,
       URL("problems",
           "read_editorial",
           args=request.args[1],
           scheme=True,
           host=True)),
        mail_type="admin",
        bulk=True)
        uetable_record.update_record(verification="accepted")
        return "ACCEPTED"
    else:
        uetable_record.update_record(verification="rejected")
        return "REJECTED"

# ----------------------------------------------------------------------------
@auth.requires_login()
def love_editorial():
    if len(request.args) == 0:
        raise HTTP(400, "Bad Request")
        return

    uetable = db.user_editorials
    editorial = db(uetable.id == int(request.args[0])).select().first()
    if editorial is None:
        raise HTTP(400, "Bad Request")
        return

    votes = set(editorial.votes.split(","))
    votes.add(str(session.user_id))
    votes.remove("") if "" in votes else ""
    editorial.update_record(votes=",".join(votes))
    return dict(love_count=len(votes))

# ----------------------------------------------------------------------------
def tag():
    """
        Tag search page
    """

    table = TABLE(_class="bordered centered")
    thead = THEAD(TR(TH(T("Problem Name")),
                     TH(T("Problem URL")),
                     TH(T("Site")),
                     TH(T("Accuracy")),
                     TH(T("Users solved")),
                     TH(T("Tags"))))
    table.append(thead)

    ttable = db.tag
    generalized_tags = db(ttable).select(ttable.value, orderby=ttable.value)
    generalized_tags = [x.value for x in generalized_tags]

    # If URL does not have vars containing q
    # then remain at the search page and return
    # an empty table
    q = request.vars.get("q", None)
    clubbed_tags = request.vars.get("generalized_tags", None)
    clubbed_tags = None if clubbed_tags == "" else clubbed_tags
    if q is None and not clubbed_tags:
        return dict(table=table, generalized_tags=generalized_tags)

    try:
        sites = request.vars.get("site", "")
        if sites == "":
            sites = []
        elif isinstance(sites, str):
            sites = [sites]
    except:
        sites = []

    orderby = request.vars.get("orderby", None)
    if orderby not in ("accuracy-asc", "accuracy-desc",
                       "solved-count-asc", "solved-count-desc"):
        orderby = None

    try:
        curr_page = int(request.vars["page"])
    except:
        curr_page = 1
    PER_PAGE = current.PER_PAGE

    ptable = db.problem
    query = True

    if q is not None and not clubbed_tags:
        # Enables multiple space seperated tag search
        q = q.split(" ")
        for tag in q:
            if tag == "":
                continue
            # Decision to make & or |
            # & => Search for problem containing all these tags
            # | => Search for problem containing one of the tags
            query &= ptable.tags.contains(tag)
    else:
        clubbed_tags = [clubbed_tags] if isinstance(clubbed_tags, str) else clubbed_tags
        ttable = db.tag
        sttable = db.suggested_tags

        tag_ids = db(ttable.value.belongs(clubbed_tags)).select(ttable.id)
        tag_ids = [x.id for x in tag_ids]

        problem_ids = db(sttable.tag_id.belongs(tag_ids)).select(sttable.problem_id)
        problem_ids = [x.problem_id for x in problem_ids]

        query &= ptable.id.belongs(problem_ids)


    site_query = None
    for site in sites:
        if site_query is not None:
            site_query |= ptable.link.contains(current.SITES[site])
        else:
            site_query = ptable.link.contains(current.SITES[site])
    if site_query:
        query &= site_query

    accuracy_column = (ptable.solved_submissions * 1.0 / ptable.total_submissions)
    kwargs = dict(distinct=True,
                  limitby=((curr_page - 1) * PER_PAGE,
                           curr_page * PER_PAGE))
    if orderby and orderby.__contains__("accuracy"):
        query &= ~(ptable.link.contains("hackerrank.com"))
        kwargs["orderby"] = ~accuracy_column if orderby == "accuracy-desc" else accuracy_column

    if orderby and orderby.__contains__("solved-count"):
        kwargs["reverse"] = True if orderby == "solved-count-desc" else False

    query &= (ptable.solved_submissions != None)
    query &= (ptable.total_submissions != None) & (ptable.total_submissions != 0)
    query &= (ptable.user_ids != None)
    query &= (ptable.custom_user_ids != None)

    total_problems = db(query).count()
    total_pages = total_problems / PER_PAGE
    if total_problems % PER_PAGE != 0:
        total_pages = total_problems / PER_PAGE + 1

    if request.extension == "json":
        return dict(total_pages=total_pages)

    if orderby and orderby.__contains__("solved-count"):
        all_problems = db(query).select(cache=(cache.ram, 3600),
                                        cacheable=True).as_list()
        all_problems.sort(key=lambda x: x["user_count"] + \
                                        x["custom_user_count"],
                          reverse=kwargs["reverse"])
        all_problems = all_problems[kwargs["limitby"][0]:kwargs["limitby"][1]]
    else:
        # No need of caching here
        all_problems = db(query).select(**kwargs)

    tbody = TBODY()
    for problem in all_problems:
        tr = TR()
        link_class = utilities.get_link_class(problem["link"], session.user_id)
        link_title = (" ".join(link_class.split("-"))).capitalize()

        tr.append(TD(utilities.problem_widget(problem["name"],
                                              problem["link"],
                                              link_class,
                                              link_title)))
        tr.append(TD(A(I(_class="fa fa-link"),
                       _href=problem["link"],
                       _class="tag-problem-link",
                       _target="_blank")))
        tr.append(TD(IMG(_src=get_static_url("images/" + \
                                             utilities.urltosite(problem["link"]) + \
                                             "_small.png"),
                         _style="height: 30px; width: 30px;")))
        tr.append(TD("%.2f" % (problem["solved_submissions"]  * 100.0 / \
                               problem["total_submissions"])))
        tr.append(TD(problem["user_count"] + problem["custom_user_count"]))

        td = TD()
        all_tags = eval(problem["tags"])
        for tag in all_tags:
            td.append(DIV(A(tag,
                            _href=URL("problems",
                                      "tag",
                                      vars={"q": tag.encode("utf8"), "page": 1}),
                            _class="tags-chip",
                            _style="color: white;",
                            _target="_blank"),
                          _class="chip"))
            td.append(" ")
        tr.append(td)
        tbody.append(tr)

    table.append(tbody)

    return dict(table=table, generalized_tags=generalized_tags)


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
@auth.requires_login()
def friends_trending():
    friends, cusfriends = utilities.get_friends(session.user_id)

    # The Original IDs of duplicate custom_friends
    custom_friends = []
    for cus_id in cusfriends:
        if cus_id[1] is None:
            custom_friends.append(cus_id[0])
        else:
            custom_friends.append(cus_id[1])

    friends, custom_friends = set(friends), set(custom_friends)
    stable = db.submission
    today = datetime.datetime.today()
    # Consider submissions only after PAST_DAYS(customizable)
    # for trending problems
    start_date = str(today - datetime.timedelta(days=current.PAST_DAYS))
    query = (stable.time_stamp >= start_date) & \
            (stable.user_id.belongs(friends) | \
             stable.custom_user_id.belongs(custom_friends))
    last_submissions = db(query).select(stable.problem_name,
                                        stable.problem_link,
                                        stable.user_id,
                                        stable.custom_user_id)

    return utilities.compute_trending_table(last_submissions,
                                            "friends",
                                            session.user_id)

# ----------------------------------------------------------------------------
def global_trending():
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
    return utilities.compute_trending_table(last_submissions, "global")

# ----------------------------------------------------------------------------
def trending():
    """
        Show trending problems globally and among friends
        @ToDo: Needs lot of comments explaining the code
    """

    if auth.is_logged_in():
        # Show table with trending problems amongst friends
        div = DIV(DIV("",
                      _id="friends-trending-table",
                      _class="col offset-s1 s4 z-depth-2",
                      _style="padding: 200px;"),
                  DIV("",
                      _id="global-trending-table",
                      _class="col offset-s2 s4 z-depth-2",
                      _style="padding: 200px;"),
                  _class="row col s12")
    else:
        # Show table with globally trending problems
        div = DIV(DIV("",
                      _id="global-trending-table",
                      _class="col offset-s1 s10 z-depth-2",
                      _style="padding: 200px;"),
                  _class="row center")

    return dict(div=div)

# ==============================================================================
