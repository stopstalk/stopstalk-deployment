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

ptable = db.problem_tags
stable = db.submission

plinks = db(ptable.problem_name == "").select(ptable.problem_link)
plinks = [x["problem_link"] for x in plinks]

splinks = db(stable).select(stable.problem_link, stable.problem_name)

all_problems = {}
for problem in splinks:
    all_problems[problem["problem_link"]] = problem["problem_name"].strip()

for plink in plinks:
    if all_problems.has_key(plink) and all_problems[plink] != "":
        query = (ptable.problem_link == plink)
        print plink, "*", all_problems[plink], "*"
        db(query).update(problem_name=all_problems[plink])
