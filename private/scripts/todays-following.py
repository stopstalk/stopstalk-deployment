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

trtable = db.todays_requests
atable = db.auth_user

user_details = {}

all_users = db(atable).select(atable.id,
                              atable.first_name,
                              atable.last_name,
                              atable.email,
                              atable.stopstalk_handle)

for user in all_users:
    user_details[user.id] = {"name": user.first_name + " " + user.last_name,
                             "email": user.email,
                             "stopstalk_handle": user.stopstalk_handle}

rows = db(trtable).select()
added_unfriended = {}

for row in rows:
    if added_unfriended.has_key(row.user_id):
        if row.transaction_type == "add":
            added_unfriended[row.user_id][0].add(row.follower_id)
        else:
            added_unfriended[row.user_id][1].add(row.follower_id)
    else:
        if row.transaction_type == "add":
            added_unfriended[row.user_id] = [set([row.follower_id]), set([])]
        else:
            added_unfriended[row.user_id] = [set([]), set([row.follower_id])]

def get_html_content(user_id, add_unfriend_list):

    added, unfriended = add_unfriend_list
    if len(added) + len(unfriended) == 0:
        return "FAILURE"

    html_message = "<html>Hey %s,<br/><br/>" % user_details[user_id]["stopstalk_handle"]

    if len(added):
        html_message += "%s" % (", ".join([str(A(user_details[x]["name"],
                                                 _href=URL("user",
                                                           "profile",
                                                           args=user_details[x]["stopstalk_handle"],
                                                           scheme="https",
                                                           host="www.stopstalk.com"))) for x in added]))
        html_message += " added you as a friend<br/><br/>"
    if len(unfriended):
        html_message += "%s" % (", ".join([str(A(user_details[x]["name"],
                                                 _href=URL("user",
                                                           "profile",
                                                           args=user_details[x]["stopstalk_handle"],
                                                           scheme="https",
                                                           host="www.stopstalk.com"))) for x in unfriended]))
        html_message += " unfriended you <br/><br/>"

    html_message += """
Adjust your email preferences %s<br/>
Cheers,<br/>
Team StopStalk
</html>
                    """ % (A("here",
                             _href=URL("default",
                                       "unsubscribe",
                                       scheme="https",
                                       host="www.stopstalk.com")))
    return html_message

for user_id in added_unfriended:
    mail_content = get_html_content(user_id, added_unfriended[user_id])
    curr_list = added_unfriended[user_id]
    if mail_content != "FAILURE":
        log_string = user_details[user_id]["name"]
        if len(curr_list[0]):
            log_string += " A:" + ",".join(str(x) for x in curr_list[0])
        if len(curr_list[1]):
            log_string += " U:" + ",".join(str(x) for x in curr_list[1])
        print log_string
        current.send_mail(to=user_details[user_id]["email"],
                          subject="Friendship activity from StopStalk",
                          message=mail_content,
                          mail_type="friend_unfriend",
                          bulk=True)

trtable.truncate()
