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

import datetime
import utilities

# ----------------------------------------------------------------------------
def pie_chart_helper():
    """
        Helper function for populating pie chart with different
        submission status of a problem
    """

    problem_id = int(request.post_vars["pid"])
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
    query = (stable.problem_id == problem_id)

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

# ------------------------------------------------------------------------------
def by():
    if len(request.args) < 1:
        session.flash = "Invalid URL!"
        redirect(URL("default", "index"))

    stopstalk_handle = request.args[0]

    atable = db.auth_user
    pstable = db.problem_setters
    ptable = db.problem

    return_val = dict(stopstalk_handle=stopstalk_handle,
                      problems_count=0)

    table = TABLE(_class="bordered centered")
    thead = THEAD(TR(TH("Problem")))

    problems = utilities.get_problems_authored_by(stopstalk_handle)
    if len(problems) == 0:
        return return_val

    return_val["table"] = utilities.get_problems_table(problems,
                                                       session.user_id,
                                                       None)

    return_val["problems_count"] = len(problems)
    return return_val

# ------------------------------------------------------------------------------
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
    problem_id = request.vars["pid"]

    tltable = db.todo_list
    ptable = db.problem

    precord = ptable(problem_id)
    query = (tltable.problem_link == precord.link) & \
            (tltable.user_id == session.user_id)
    row = db(query).select().first()
    if row:
        return T("Problem already in ToDo List")
    else:
        tltable.insert(problem_link=precord.link, user_id=session.user_id)

    return T("Problem added to ToDo List")

# ----------------------------------------------------------------------------
@auth.requires_login()
def add_suggested_tags():

    sttable = db.suggested_tags
    ptable = db.problem
    ttable = db.tag

    problem_id = int(request.vars["problem_id"])
    tags = request.vars["tags"]

    today = datetime.datetime.now().strftime("%Y-%m-%d")
    problem = ptable(problem_id)
    if not problem:
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
def problem_difficulty():
    if request.env.request_method != "POST" or request.extension != "json":
        raise(HTTP(405, "Method not allowed"))
        return dict()

    problem_id = int(request.vars["problem_id"])
    score = int(request.vars["score"])
    pdtable = db.problem_difficulty
    ptable = db.problem

    query = (pdtable.user_id == session.user_id) & \
            (pdtable.problem_id == problem_id)
    pdrecord = db(query).select().first()
    if pdrecord is None:
        pdtable.insert(problem_id=problem_id,
                       score=score,
                       user_id=session.user_id)
    else:
        pdrecord.update_record(score=score)

    problem_details = utilities.get_next_problem_to_suggest(session.user_id)

    return problem_details

# ----------------------------------------------------------------------------
@auth.requires_login()
def get_next_problem_to_suggest():
    return utilities.get_next_problem_to_suggest(session.user_id,
                                                 request.vars.get("problem_id", None))

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
def get_submissions_list():
    if request.vars.has_key("problem_id") is False:
        # Disables direct entering of a URL
        session.flash = T("Please click on a Problem Link")
        redirect(URL("default", "index"))
        return

    try:
        problem_id = int(request.vars["problem_id"])
    except ValueError:
        session.flash = T("Invalid problem!")
        redirect(URL("default", "index"))
        return

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
    query = (stable.problem_id == problem_id)
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

    submissions = db(query).select(orderby=~stable.time_stamp,
                                   limitby=(0, 200))

    if len(submissions):
        table = utilities.render_table(submissions, cusfriends, session.user_id)
    else:
        table = DIV(T("No submissions found"))
    return table

# ----------------------------------------------------------------------------
def index():
    """
        The main problem page
    """
    from json import dumps

    if request.vars.has_key("problem_id") is False:
        # Disables direct entering of a URL
        session.flash = T("Please click on a Problem Link")
        redirect(URL("default", "index"))
        return

    try:
        problem_id = int(request.vars["problem_id"])
    except ValueError:
        session.flash = T("Invalid problem!")
        redirect(URL("default", "index"))
        return

    submission_type = "friends"
    if request.vars.has_key("submission_type"):
        if request.vars["submission_type"] == "global":
            submission_type = "global"
        elif request.vars["submission_type"] == "my":
            submission_type = "my"

    if auth.is_logged_in() is False and submission_type != "global":
        response.flash = T("Login to view your/friends' submissions")
        submission_type = "global"

    ptable = db.problem
    pstable = db.problem_setters

    problem_record = ptable(problem_id)
    if problem_record is None:
        session.flash = T("Please click on a Problem Link")
        redirect(URL("default", "index"))

    setters = db(pstable.problem_id == problem_id).select(pstable.handle)
    setters = [x.handle for x in setters]

    try:
        all_tags = problem_record.tags
        if all_tags:
            all_tags = eval(all_tags)
        else:
            all_tags = ["-"]
    except AttributeError:
        all_tags = ["-"]

    lower_site = utilities.urltosite(problem_record.link)
    site = utilities.get_actual_site(lower_site)
    problem_details = DIV(_class="row")
    details_table = TABLE(_style="font-size: 140%; float: left; width: 50%;")
    problem_class = ""

    link_class, link_title = utilities.get_link_class(problem_id, session.user_id)

    tbody = TBODY()
    tbody.append(TR(TD(),
                    TD(STRONG(T("Problem Name") + ":")),
                    TD(utilities.problem_widget(problem_record.name,
                                                problem_record.link,
                                                link_class,
                                                link_title,
                                                problem_id,
                                                anchor=False,
                                                disable_todo=True),
                       _id="problem_name")))
    tbody.append(TR(TD(),
                    TD(STRONG(T("Site") + ":")),
                    TD(site)))

    links = DIV(DIV(A(I(_class="fa fa-link"), " " + T("Problem"),
                      _href=problem_record.link,
                      _class="problem-page-site-link",
                      _style="color: black;",
                      _target="blank"),
                    _class="chip lime accent-3"),
                " ",
                DIV(A(I(_class="fa fa-book"), " " + T("Editorials"),
                      _href=URL("problems", "editorials", args=problem_record.id),
                      _class="problem-page-editorials",
                      _style="color: white;",
                      _target="_blank"),
                    _class="chip deep-purple darken-1",
                    _id="problem-page-editorial-button"))

    if auth.is_logged_in():
        links.append(DIV(A(I(_class="fa fa-edit"), " " + T("Suggest Difficulty"),
                             _style="color: white;"),
                         _class="chip",
                         _style="background-color: #9b4da9; cursor: pointer;",
                         _id="problem-page-difficulty-button"))
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

    if len(setters) > 0:
        tbody.append(TR(TD(),
                        TD(STRONG(T("Problem setters") + ":")),
                        TD(DIV(utilities.problem_setters_widget(setters,
                                                                site)))))

    details_table.append(tbody)
    problem_details.append(details_table)
    problem_details.append(DIV(_style="width: 50%; height: 200px; margin-top: 3%",
                               _id="chart_div",
                               _class="right"))

    return dict(site=site,
                problem_details=problem_details,
                problem_name=problem_record.name,
                problem_link=problem_record.link,
                problem_id=problem_id,
                submission_type=submission_type)

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
    user_editorials = db(query).select(orderby=~uetable.added_on)
    accepted_count = len(filter(lambda x: (x.verification == "accepted" or \
                                           (auth.is_logged_in() and \
                                            (x.user_id == session.user_id or \
                                             session.user_id in STOPSTALK_ADMIN_USER_IDS)
                                             )
                                            ),
                                user_editorials))
    if accepted_count == 0:
        if auth.is_logged_in():
            table_contents = T("No editorials found! Please contribute to the community by writing an editorial if you've solved the problem.")
        else:
            table_contents = T("No editorials found! Please login if you want to write an editorial.")

        return dict(name=record.name,
                    link=record.link,
                    editorial_link=record.editorial_link,
                    table=DIV(BR(), H6(table_contents)),
                    problem_id=record.id,
                    site=utilities.urltosite(record.link))

    user_id = session.user_id if auth.is_logged_in() else None
    table = utilities.render_user_editorials_table(user_editorials,
                                                   user_id,
                                                   user_id,
                                                   "read-editorial-problem-editorials-page")

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
    elif auth.is_logged_in() and session.user_id in STOPSTALK_ADMIN_USER_IDS:
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
                problem_id=problem.id,
                stopstalk_handle=user.stopstalk_handle,
                content=content,
                all_editorials_link=URL("problems",
                                        "editorials",
                                        args=problem.id),
                ue_record=ue_record)

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
    ptable = db.problem
    atable = db.auth_user

    uetable_record = uetable(request.args[1])
    if uetable_record.verification != "pending":
        return "Status is already updated"

    ptable_record = ptable(uetable_record.problem_id)
    user = atable(uetable_record.user_id)

    if request.args[0] == "accepted":
        current.send_mail(to=user.email,
                          subject="Your editorial for %s on StopStalk is published!" % ptable_record.name,
                          message="""
<html>
Hello %s,<br/><br/>

Your <a href="%s">editorial</a> on StopStalk is <b>Approved</b>. Thank you for your valuable contribution to the community.<br/>
Please share your editorial link on Social Media platforms or Competitive programming blogs to help other fellow friends struggling with the problem.
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
        current.REDIS_CLIENT.delete("get_dates_" + user.stopstalk_handle)
        return "ACCEPTED"
    elif request.args[0] == "rejected":
        uetable_record.update_record(verification="rejected")
        return "REJECTED"
    else:
        return "INVALID_PARAMS"

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

    redirect(URL("problems", "search", vars=request.vars))
    return

# ----------------------------------------------------------------------------
def search():
    """
        Search page for problems
    """

    ttable = db.tag
    uetable = db.user_editorials

    problem_name = request.vars.get("name", None)
    orderby = request.vars.get("orderby", None)
    clubbed_tags = request.vars.get("generalized_tags", None)
    q = request.vars.get("q", None)
    sites = request.vars.get("site", None)
    include_editorials = request.vars.get("include_editorials", "")
    exclude_solved = request.vars.get("exclude_solved", None)

    generalized_tags = db(ttable).select(ttable.value, orderby=ttable.value)
    generalized_tags = [x.value for x in generalized_tags]

    if any([problem_name, orderby, clubbed_tags, q, sites]) is False:
        if request.extension == "json":
            return dict(total_pages=0)
        else:
            if len(request.get_vars):
                # No filter is applied
                response.flash = "No filter is applied"
            return dict(table=DIV(), generalized_tags=generalized_tags)

    clubbed_tags = None if clubbed_tags == "" else clubbed_tags

    try:
        if sites == None or sites == "":
            sites = []
        elif isinstance(sites, str):
            sites = [sites]
    except:
        sites = []

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

    rows = db(uetable.verification == "accepted").select(uetable.problem_id)
    problem_with_user_editorials = set([x["problem_id"] for x in rows])

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
    elif clubbed_tags:
        clubbed_tags = [clubbed_tags] if isinstance(clubbed_tags, str) else clubbed_tags
        ttable = db.tag
        sttable = db.suggested_tags

        tag_ids = db(ttable.value.belongs(clubbed_tags)).select(ttable.id)
        tag_ids = [x.id for x in tag_ids]

        problem_ids = db(sttable.tag_id.belongs(tag_ids)).select(sttable.problem_id)
        problem_ids = [x.problem_id for x in problem_ids]

        query &= ptable.id.belongs(problem_ids)

    if problem_name:
        query &= ptable.name.contains(problem_name)

    if include_editorials:
        # Check if the site editorial link is present or the problem id exists
        # in user_editorials table with accepted status
        query &= (((ptable.editorial_link != None) & \
                   (ptable.editorial_link != "")) | \
                  (ptable.id.belongs(problem_with_user_editorials)))

    if exclude_solved and auth.is_logged_in():
        solved_pids, _ = utilities.get_solved_problems(session.user_id, False)
        query &= ~ptable.id.belongs(solved_pids)
    elif exclude_solved and request.extension == "html":
        response.flash = T("Login to apply this filter")

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

    if request.extension == "json":
        total_problems = db(query).count()

        total_pages = total_problems / PER_PAGE
        if total_problems % PER_PAGE != 0:
            total_pages = total_problems / PER_PAGE + 1

        return dict(total_pages=total_pages)

    if orderby and orderby.__contains__("solved-count"):
        all_problems = db(query).select().as_list()
        all_problems.sort(key=lambda x: x["user_count"] + \
                                        x["custom_user_count"],
                          reverse=kwargs["reverse"])
        all_problems = all_problems[kwargs["limitby"][0]:kwargs["limitby"][1]]
    else:
        # No need of caching here
        all_problems = db(query).select(**kwargs)

    return dict(table=utilities.get_problems_table(all_problems,
                                                   session.user_id,
                                                   problem_with_user_editorials),
                generalized_tags=generalized_tags)

# ----------------------------------------------------------------------------
@auth.requires_login()
def friends_trending():
    import trending_utilities
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
    query = (stable.user_id.belongs(friends) | \
             stable.custom_user_id.belongs(custom_friends))
    last_submissions = trending_utilities.get_last_submissions_for_trending(query)

    return trending_utilities.compute_trending_table(last_submissions,
                                                     "friends",
                                                     session.user_id)

# ----------------------------------------------------------------------------
def global_trending():
    from trending_utilities import draw_trending_table
    trending_problems = current.REDIS_CLIENT.get(GLOBALLY_TRENDING_PROBLEMS_CACHE_KEY)
    trending_problems = eval(trending_problems)
    return draw_trending_table(trending_problems, "global", session.user_id)

# ----------------------------------------------------------------------------
def trending():
    """
        Show trending problems globally and among friends
    """

    if auth.is_logged_in():
        # Show table with trending problems amongst friends
        div = DIV(DIV("",
                      _id="friends-trending-table",
                      _class="col offset-s1 s4 z-depth-2 trendings-html-table",
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
                      _class="col offset-s3 s6 z-depth-2 trendings-html-table",
                      _style="padding: 200px;"),
                  _class="row center")

    return dict(div=div)

# ----------------------------------------------------------------------------
@auth.requires_login()
def recommendations():
    """
        Problem recommendations for the user.
    """
    import recommendations.problems as recommendations
    import stopstalk_constants

    ptable = db.problem
    rtable = db.problem_recommendations
    user_id = session.user_id
    refresh = request.vars.get("refresh", "false") == "true"

    output = {}
    recommendation_pids = []

    rows = db(rtable.user_id == user_id).select()
    if rows is None or len(rows.as_list()) == 0:
        refresh = True

    if refresh:
        recommendation_pids = recommendations.generate_recommendations(user_id)
    else:
        recommendation_pids, _ = recommendations.retrieve_past_recommendations(user_id)

    if recommendation_pids is not None and len(recommendation_pids) > 0:
        problem_details = db(ptable.id.belongs(recommendation_pids)).select().as_list()
        output["table"] = utilities.get_problems_table(problem_details, user_id)
    else:
        output["table"] = "No recommendations available."

    query = (rtable.user_id == user_id) & (rtable.is_active == True)
    rows = db(query).select(rtable.generated_at)

    output["can_update"] = True
    if rows is not None and len(rows) > 0:
        output["can_update"] = (datetime.datetime.now().date() - rows[0].generated_at).days \
            >= stopstalk_constants.RECOMMENDATION_REFRESH_INTERVAL

    return output

# ----------------------------------------------------------------------------
@auth.requires_login()
def update_recommendation_status():
    from recommendations.problems import update_recommendation_status

    pid = long(request.args[0])
    update_recommendation_status(session.user_id, pid)

# ==============================================================================
