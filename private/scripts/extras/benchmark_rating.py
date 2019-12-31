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

import utilities
stable = db.submission
atable = db.auth_user
BATCH_SIZE = 100
attempted_list = []
solved_list = []
accuracy_list = []

last_id = db(atable).select(orderby=~atable.id).first().id
for i in xrange(1, last_id):
    solved, unsolved = utilities.get_solved_problems(i)
    solved = len(solved)
    unsolved = len(unsolved)
    submissions = db(stable.user_id == i).select(stable.status)
    submissions = [x.status for x in submissions]
    try:
        accuracy = submissions.count("AC") * 100.0 / len(submissions)
    except:
        accuracy = 0
    attempted_list.append(unsolved)
    solved_list.append(solved)
    accuracy_list.append(accuracy)
    print i, solved, unsolved, accuracy

print "_______________________________"
print attempted_list
print "_______________________________"
print solved_list
print "_______________________________"
print accuracy_list
print "_______________________________"
