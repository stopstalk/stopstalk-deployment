"""
    Copyright (c) 2015 Raj Patel(raj454raj@gmail.com), StopStalk

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

from gluon import *
import time
from datetime import datetime, date

# -----------------------------------------------------------------------------
def get_link(site, handle):
    """
        Get the URL of site_handle
    """

    return current.SITES[site] + handle

# -----------------------------------------------------------------------------
def get_friends(user_id):
    """
        Friends of user_id (including custom friens)

        @Return: (list of friend_ids, list of custom_friend_ids)
    """

    db = current.db
    cftable = db.custom_friend
    atable = db.auth_user
    ftable = db.friends

    # Retrieve custom friends
    query = (cftable.user_id == user_id)
    custom_friends = db(query).select(cftable.id)
    custom_friends = map(lambda x: x["id"], custom_friends)

    # Retrieve friends
    query = (ftable.user_id == atable.id)
    friend_ids = db(atable.id != user_id).select(atable.id, join=ftable.on(query))
    friends = map(lambda x: x["id"], friend_ids)

    return friends, custom_friends

# -----------------------------------------------------------------------------
def materialize_form(form, fields):
    """
        Change layout of SQLFORM forms
    """

    form.add_class("form-horizontal center")
    main_div = DIV(_class="center")

    for id, label, controls, help in fields:
        curr_div = DIV(_class="row")
        input_field = None
        _controls = controls

        try:
            _name = controls.attributes["_name"]
        except:
            _name = ""
        try:
            _type = controls.attributes["_type"]
        except:
            _type = "string"

        try:
            _id = controls.attributes["_id"]
        except:
            _id = ""

        if isinstance(controls, INPUT):
            if _type == "file":
                # Layout for file type inputs
                input_field = DIV(DIV(SPAN("Upload"),
                                      INPUT(_type=_type,
                                            _id=_id),
                                      _class="btn"),
                                  DIV(INPUT(_type="text",
                                            _class="file-path",
                                            _placeholder=label.components[0]),
                                      _class="file-path-wrapper"),
                                  _class="col input-field file-field offset-s3 s6")
        if isinstance(controls, SPAN):
            # Mostly for ids which cannot be edited by user
            _controls = INPUT(_value=controls.components[0],
                              _id=_id,
                              _name=_name,
                              _disabled="disabled")
        elif isinstance(controls, TEXTAREA):
            # Textarea inputs
            try:
                _controls = TEXTAREA(controls.components[0],
                                     _name=_name,
                                     _id=_id,
                                     _class="materialize-textarea text")
            except IndexError:
                _controls = TEXTAREA(_name=_name,
                                     _id=_id,
                                     _class="materialize-textarea text")
        elif isinstance(controls, SELECT):
            # Select inputs
            _controls = SELECT(OPTION(label, _value=""),
                               _name=_name,
                               *controls.components[1:]
                               )
            # Note now label will be the first element
            # of Select input whose value would be ""
            label = ""
        elif isinstance(controls, A):
            # For the links in the bottom while updating tables like auth_user
            label = ""
        elif isinstance(controls, INPUT) is False:
            # If the values are readonly
            _controls = INPUT(_value=controls,
                              _name=_name,
                              _disabled="")

        if input_field is None:
            input_field = DIV(_controls, label,
                              _class="input-field col offset-s3 s6")

        curr_div.append(input_field)
        main_div.append(curr_div)

    return main_div

# -----------------------------------------------------------------------------
def render_table(submissions):
    """
        Create the HTML table from submissions
    """

    status_dict = {"AC": "Accepted",
                   "WA": "Wrong Answer",
                   "TLE": "Time Limit Exceeded",
                   "MLE": "Memory Limit Exceeded",
                   "RE": "Runtime Error",
                   "CE": "Compile Error",
                   "SK": "Skipped",
                   "HCK": "Hacked",
                   "OTH": "Others",
                   }

    table = TABLE(_class="striped centered")
    table.append(THEAD(TR(TH("User Name"),
                          TH("Site"),
                          TH("Site Handle"),
                          TH("Time of submission"),
                          TH("Problem"),
                          TH("Language"),
                          TH("Status"),
                          TH("Points"),
                          TH("View Code"))))

    tbody = TBODY()
    for submission in submissions:
        tr = TR()
        append = tr.append

        person_id = submission.custom_user_id
        if submission.user_id:
            person_id = submission.user_id

        append(TD(A(person_id.first_name + " " + person_id.last_name,
                    _href=URL("user", "profile",
                              args=[submission.stopstalk_handle]),
                    _target="_blank")))
        append(TD(submission.site))
        append(TD(A(submission.site_handle,
                    _href=get_link(submission.site,
                                   submission.site_handle),
                    _target="_blank")))
        append(TD(submission.time_stamp))
        append(TD(A(submission.problem_name,
                    _href=URL("problems",
                              "index",
                              vars={"pname": submission.problem_name,
                                    "plink": submission.problem_link}),
                    _target="_blank")))
        append(TD(submission.lang))
        append(TD(IMG(_src=URL("static",
                               "images/" + submission.status + ".jpg"),
                      _title=status_dict[submission.status],
                      _style="height: 25px; width: 25px;")))
        append(TD(submission.points))

        if submission.view_link:
            append(TD(A("View",
                        _href=submission.view_link,
                        _class="btn waves-light waves-effect",
                        _style="background-color: #FF5722",
                        _target="_blank")))
        else:
            append(TD())

        tbody.append(tr)
    table.append(tbody)
    return table
