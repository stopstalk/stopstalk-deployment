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

"""
challenge --> challenges --> problem --> practice

Cases handled -
1. If practice is present and not 404 then change challenge, challenges and problem to practice
2. If problem is present and not 404 then change challenge, challenges to problem
3. If just challenge and challenges then change challenge to challenges
4. If not hackerearth.com/(challenge|challenges|practice|problem) then use the problem/practice one
"""
import re
import requests
import utilities
import datetime

ptable = db.problem

similar_problems = {}
this_points_to_that = {}

def get_slug_from_link(link, count):
    return "/".join(link.split("/")[-count:])

def find_pairs(values):
    result = []
    final_problem_id = None
    final_problem_link = None
    print values.keys()
    if "practice" in values:
        if len(values["practice"]) > 1:
            for problem_record in values["practice"]:
                response = requests.get(problem_record.link)
                if response.status_code == 200 and response.url == problem_record.link:
                    final_problem_id = problem_record.id
                    final_problem_link = problem_record.link
                    break
        else:
            problem_record = values["practice"][0]
            response = requests.get(problem_record.link)
            if response.status_code == 200:
                final_problem_id = problem_record.id
                final_problem_link = problem_record.link

    if final_problem_id is None and "problem" in values:
        problem_record = values["problem"][0]
        response = requests.get(problem_record.link)
        if response.status_code == 200 and response.url == problem_record.link:
            final_problem_id = problem_record.id
            final_problem_link = problem_record.link

    if final_problem_id is None and "challenges" in values:
        final_problem_id = values["challenges"][0].id
        final_problem_link = values["challenges"][0].link

    if final_problem_id is None and "challenge" in values:
        final_problem_id = values["challenge"][0].id
        final_problem_link = values["challenge"][0].link

    if final_problem_id is None and "something_else" in values:
        final_problem_id = values["something_else"][0].id
        final_problem_link = values["something_else"][0].link

    if final_problem_id is None:
        if values.keys() == ["problem", "practice"]:
            values["problem"][0].delete_record()
            values["practice"][0].delete_record()
        else:
            print "Couldn't find problem record for", values
        return

    for key in values:
        for problem in values[key]:
            print problem.link, "-->", final_problem_link
            print problem.id, "-->", final_problem_id
            utilities.merge_duplicate_problems(final_problem_id, problem.id)

rows = db(ptable.link.contains("hackerearth.com/")).select()

for row in rows:
    key = get_slug_from_link(row.link, 3)
    if key in similar_problems:
        similar_problems[key].append(row)
    else:
        similar_problems[key] = [row]

print str(datetime.datetime.now()), "Starting to clean HackerEarth duplicates"

all_set = set([])
for key in similar_problems:
    if len(similar_problems[key]) > 1:
        values = {}
        for item in similar_problems[key]:
            try:
                tmp_val = re.match("https://www.hackerearth.com/.*?/",
                                   item.link).group()
            except AttributeError:
                print "Exception in matching", item.link
                values = {}
                break

            tmp_val = get_slug_from_link(tmp_val, 2)[:-1]
            tmp_val = "something_else" if tmp_val not in ("challenges", "challenge", "practice", "problem") else tmp_val
            if tmp_val in values:
                values[tmp_val].append(item)
            else:
                values[tmp_val] = [item]
        find_pairs(values)
        print "__________________________________________________"

print str(datetime.datetime.now()), "End cleaning HackerEarth duplicates"
