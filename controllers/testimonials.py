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

def index():
    ttable = db.testimonials
    if auth.is_logged_in():
        testimonial_content = request.vars.get("testimonial_content", None)
        if testimonial_content:
            testimonial_content = testimonial_content.strip()
            testimonial_id = ttable.insert(content=testimonial_content,
                                           verification="pending",
                                           user_id=session.user_id,
                                           stars="",
                                           created_at=str(datetime.datetime.now())[:-7])
            current.send_mail(to="raj454raj@gmail.com",
                              subject="New testimonial by " + session.handle,
                              message="""<html>
                                            %s<br/>
                                            <a href='%s'>Approve</a>
                                            <a href='%s'>Reject</a>
                                         </html>""" % (testimonial_content,
                                                       URL("testimonials",
                                                           "admin_approval",
                                                           args=["approved", testimonial_id],
                                                           scheme=True,
                                                           host=True),
                                                       URL("testimonials",
                                                           "admin_approval",
                                                           args=["rejected", testimonial_id],
                                                           scheme=True,
                                                           host=True)),
                              mail_type="admin",
                              bulk=True)
            session.flash = "Submitted for Admin Approval"
            redirect(URL("testimonials", "index"))


    testimonials = db(ttable.verification == "approved").select(orderby=~ttable.id)
    testimonial_details = {}
    strptime = datetime.datetime.strptime
    for testimonial in testimonials:
        testimonial_details[testimonial.id] = (testimonial.created_at.strftime("%H:%M, %d %B, %Y"),
                                               db.auth_user(testimonial.user_id).stopstalk_handle)
    return dict(testimonials=testimonials,
                testimonial_details=testimonial_details)

@auth.requires_login()
def love_testimonial():

    if len(request.args) == 0:
        raise HTTP(400, "Bad Request")
        return

    ttable = db.testimonials
    testimonial = db(ttable.id == request.args[0]).select().first()
    if testimonial is None:
        raise HTTP(400, "Bad Request")
        return

    stars = set(testimonial.stars.split(","))
    stars.add(str(session.user_id))
    stars.remove("") if "" in stars else ""
    testimonial.update_record(stars=",".join(stars))

    return dict(love_count=len(stars))

@auth.requires_login()
def admin_approval():
    if session.user_id != 1:
        return "You shouldn't be here"
    else:
        if len(request.args) != 2:
            return "Invalid params"
        ttable = db.testimonials
        row = db(ttable.id == request.args[1]).select().first()
        if row:
            row.update_record(verification=request.args[0])
            user = db.auth_user(int(row.user_id))
            if request.args[0] == "approved":
                current.send_mail(to=user.email,
                                  subject="Your Testimonial on StopStalk",
                                  message="""<html>Hey %s, <br/><br/>
This is to inform you that we have approved your Testimonial and published it on StopStalk.
Check it out on the <a href="%s">Testimonials Page</a>.<br/><br/>
Cheers,<br/>
Team StopStalk
</html>
""" % (user.stopstalk_handle,
       URL("testimonials", "index", host=True, scheme=True)),
                                  mail_type="feature_updates",
                                  bulk=True)
        return "Successfully updated"

# ==============================================================================
