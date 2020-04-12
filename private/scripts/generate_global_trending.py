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

# Done here because the number of submissions in last current.PAST_DAYS is too
# huge for a request to process in 60 seconds

import time
import trending_utilities

db = current.db
stable = db.submission
query = (stable.custom_user_id == None)

start = time.time()
last_submissions = trending_utilities.get_last_submissions_for_trending(query)
print datetime.datetime.now(), "Got submissions for last", current.PAST_DAYS, "days in ", time.time() - start, "seconds"
print datetime.datetime.now(), "Total submission count:", len(last_submissions)
trending_problems = trending_utilities.get_trending_problem_list(last_submissions)

current.REDIS_CLIENT.set(GLOBALLY_TRENDING_PROBLEMS_CACHE_KEY,
                         str(trending_problems))

print datetime.datetime.now(), "Redis set done on", GLOBALLY_TRENDING_PROBLEMS_CACHE_KEY
