"""
    Copyright (c) 2015-2019 Raj Patel(raj454raj@gmail.com), StopStalk

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
import requests
import time
from sites.init import *

user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36"
ptable = db.problem

result = db.executesql("""
    SELECT substring_index(link, "/", -1), group_concat(id)
    FROM problem
    WHERE link LIKE "%www.codechef.com%"
    GROUP BY 1
    HAVING COUNT(*) > 1;
""")

print "Evaluating", len(result), "duplicate records"

for row in result:

    problem_ids = [int(x) for x in row[1].split(",")]
    temp_records = db(ptable.id.belongs(problem_ids)).select()
    problem_records = {}
    for problem_record in temp_records:
        problem_records[problem_record.id] = problem_record

    final_problem_id = None
    final_problem_link = None

    duplicates = []

    for problem_id in problem_ids:
        precord = problem_records[problem_id]
        url = precord.link
        url_value = url.replace("https://www.codechef.com/", "https://www.codechef.com/api/contests/")
        response = get_request(url_value + "?v=1554915627060",
                               headers={"User-Agent": user_agent})
        response = response.json()
        if response["status"] != "error" and \
           (final_problem_id is None or url.__contains__("/PRACTICE/")):

                if final_problem_id is not None:
                    duplicates.append(final_problem_id)

                final_problem_id = problem_id
                final_problem_link = url

        if final_problem_id != problem_id:
            duplicates.append(problem_id)

    if final_problem_id is not None:
        for duplicate_id in duplicates:
            print problem_records[duplicate_id].link, "-->", final_problem_link
            utilities.merge_duplicate_problems(final_problem_id, duplicate_id)
    else:
        print problem_ids, "no original found"

    time.sleep(1)

    print "******************************"

