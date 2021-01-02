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

stable = db.submission
user_id = 1
rows = db(stable.user_id == user_id).select(stable.time_stamp,
                                            stable.problem_link,
                                            stable.status,
                                            orderby=stable.time_stamp)

solved_problem_links = set([])
total_submissions = 0
final_rating = {}
curr_streak = 1
max_streak = 1
rating = 0
INITIAL_DATE = datetime.datetime.strptime(current.INITIAL_DATE,
                                          "%Y-%m-%d %H:%M:%S").date()
prev_date = INITIAL_DATE

def compute_prev_day_rating(date):
    if total_submissions == 0:
        return
    global rating
    solved = len(solved_problem_links)
    curr_per_day = total_submissions * 1.0 / ((date - INITIAL_DATE).days + 1)
    rating = max_streak * 50 + \
             solved * 100 + \
             (solved * 100.0 / total_submissions) * 80 + \
             (total_submissions - solved) * 15 + \
             curr_per_day * 8000
             #per_day * 2000
    print "Previous date:", str(date)
    print "#Solved:", solved
    print "Total Submissions:", total_submissions
    print "Current streak:", curr_streak
    print "Maximum streak:", max_streak
    print "curr_per_day:", curr_per_day
    print "Rating: ", rating
    print "*****************************************************"
    final_rating[str(date)] = rating


for row in rows:
    curr_date = row["time_stamp"].date()
    number_of_dates = (curr_date - prev_date).days
    for cnt in xrange(number_of_dates):
        compute_prev_day_rating(prev_date + datetime.timedelta(days=cnt))
    print "____________________", row.time_stamp, row.problem_link, row.status, "____________________________"
    if prev_date != curr_date:
        if prev_date is not None and (curr_date - prev_date).days == 1:
            curr_streak += 1
            if curr_streak > max_streak:
                max_streak = curr_streak
        else:
            curr_streak = 1

        # compute rating of prev_date
    if row["status"] == "AC":
        solved_problem_links.add(row["problem_link"])
    total_submissions += 1
    prev_date = curr_date

number_of_dates = (datetime.datetime.now().date() - prev_date).days
for cnt in xrange(number_of_dates):
    compute_prev_day_rating(prev_date + datetime.timedelta(days=cnt))
# print final_rating
for key in final_rating:
    print key, final_rating[key]
