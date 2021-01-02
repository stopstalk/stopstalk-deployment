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

# +++++++++++++++++++++++++++++++++++++
# DEPRECATED after adding problem table
# +++++++++++++++++++++++++++++++++++++

import requests
from bs4 import BeautifulSoup

def retrieve_pname(problem_link):
    response = requests.get(problem_link)
    if response.status_code != 200:
        print problem_link, response.status_code
        return -1
    soup = BeautifulSoup(response.text, "lxml")
    title = soup.find("title").contents[0]
    if title.__contains__("Problem"):
        pname = soup.find(class_="title").contents[0]
        return pname[3:]
    else:
        return "problem moved"

ptable = db.problem_tags
stable = db.submission

res = db(stable.problem_name=="").select()

name_dict = {}

# Store the ids of the users and custom users whose codeforces
# submissions are corrupted due to the unicode issue
users = set([])
custom_users = set([])

for submission in res:
    if submission.problem_link.__contains__("gymProblem"):
        if submission.user_id:
            users.add(submission.user_id)
        elif submission.custom_user_id:
            custom_users.add(submission.custom_user_id)
        else:
            print "Something is wrong",
    else:
        print "{",
        if name_dict.has_key(submission.problem_link):
            submission.update_record(problem_name=name_dict[submission.problem_link])
            print submission.problem_link, name_dict[submission.problem_link],
        else:
            pname = retrieve_pname(submission.problem_link)
            print submission.problem_link, "*", pname, "*",
            if pname != -1 and pname != "problem moved":
                submission.update_record(problem_name=pname)
                name_dict[submission.problem_link] = pname
            elif pname == "problem moved":
                print "Deleted", submission,
                submission.delete_record()
        print "}"

query = (ptable.problem_link.belongs(name_dict.keys())) & \
        (ptable.problem_name == "")

db(query).delete()

print users, custom_users
# Initialize the users back to initial state
attrs = dict(last_retrieved=current.INITIAL_DATE,
             rating=0,
             per_day=0.0)
db(db.auth_user.id.belongs(users)).update(**attrs)
db(db.custom_friend.id.belongs(custom_users)).update(**attrs)

# Delete all the submissions of the users which
# which have corrupted CodeForces submissions
db(stable.user_id.belongs(users)).delete()
db(stable.custom_user_id.belongs(custom_users)).delete()
