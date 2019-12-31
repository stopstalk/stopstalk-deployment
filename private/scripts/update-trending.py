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

"""
    ****************************************
               NO LONGER IN USE
    ****************************************
    Proof of how bad code was used for very simple problem
    which ran in a CRON for more than an hour ;)
"""

import gevent
from gevent import monkey
gevent.monkey.patch_all(thread=False)

import datetime

# ----------------------------------------------------------------------------
def _get_total_users(trending_problems,
                     start_date,
                     end_date):

    def _perform_query(problem, start_date):
        sql = """
                 SELECT COUNT(id)
                 FROM `submission`
                 WHERE ((problem_link = '%s')
                   AND  (time_stamp >= '%s'))
                 GROUP BY user_id, custom_user_id
              """ % (problem["submission"]["problem_link"],
                     start_date)
        res = db.executesql(sql)
        problem["unique"] = len(res)

    threads = []
    for problem in trending_problems:
        threads.append(gevent.spawn(_perform_query, problem, start_date))

    gevent.joinall(threads)

    return trending_problems

# ----------------------------------------------------------------------------
if __name__ == "__main__":

    db = current.db
    stable = db.submission
    tptable = db.trending_problems

    today = datetime.datetime.today()
    # Consider submissions only after PAST_DAYS(customisable)
    # for trending problems
    start_date = str(today - datetime.timedelta(days=current.PAST_DAYS))
    end_date = str(today)
    count = stable.id.count()

    query = (stable.time_stamp >= start_date)
    query &= (stable.time_stamp <= end_date)
    # @Todo: Investigate the need for this db query
    global_trending = db(query).select(stable.problem_name,
                                       stable.problem_link,
                                       count,
                                       orderby=~count,
                                       groupby=stable.problem_link)
    global_trending = _get_total_users(global_trending.as_list(),
                                       start_date,
                                       end_date)
    # Sort the rows according to the
    # number of users who solved the
    # problem in last PAST_DAYS
    global_trending = sorted(global_trending,
                             key=lambda k: k["unique"],
                             reverse=True)

    global_trending = global_trending[:current.PROBLEMS_PER_PAGE]

    # Empty the table first
    tptable.truncate()

    # @Todo: Bulk insert please!
    for row in global_trending:
        tptable.insert(problem_name=row["submission"]["problem_name"],
                       problem_link=row["submission"]["problem_link"],
                       submission_count=row["_extra"]["COUNT(submission.id)"],
                       user_count=row["unique"])
