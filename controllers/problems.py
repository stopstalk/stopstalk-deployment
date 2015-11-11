import utilities
import profilesites as profile

def pie_chart_helper():

    problem_name = request.post_vars["pname"]
    stable = db.submission
    count = stable.id.count()
    row = db(stable.problem_name == problem_name).select(stable.status,
                                                         count,
                                                         groupby=stable.status)
    return dict(row=row)

def index():

    if len(request.args) < 1:
        session.flash = "Please click on a Problem Link"
        redirect(URL("default", "index"))
    stable = db.submission
    submission = db(stable.id == request.args[0]).select().first()
    if submission:
        problem_name = submission.problem_name
        problem_link = submission.problem_link
        submissions = db(stable.problem_name == problem_name).select(orderby=~stable.time_stamp)
        try:
            tags_func = getattr(profile, submission.site.lower() + "_get_tags")
            all_tags = tags_func(problem_link)
            if all_tags != []:
                tags = DIV()
                for tag in all_tags:
                    tags.append(DIV(tag, _class="chip"))
                    tags.append(" ")
            else:
                tags = DIV("No tags available")
        except AttributeError:
            tags = DIV("No tags available")

        problem_details = TABLE(_style="float: left; width: 30%; margin-top: 12%; margin-left: 8%; font-size: 150%;")
        tbody = TBODY()
        tbody.append(TR(TD(STRONG("Problem Name:"),
                        TD(problem_name,
                           _id="problem_name"))))
        tbody.append(TR(TD(STRONG("Problem Link:"),
                        TD(A(I(_class="fa fa-link"), " Link",
                             _href=problem_link)))))
        tbody.append(TR(TD(STRONG("Tags:")),
                       (TD(tags))))
        problem_details.append(tbody)
        table = utilities.render_table(submissions)

    else:
        session.flash = "Invalid problem link"
        redirect(URL("default", "index"))

    return dict(problem_details=problem_details,
                problem_name=problem_name,
                problem_link=problem_link,
                table=table)
