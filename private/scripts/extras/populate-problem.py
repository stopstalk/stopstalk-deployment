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

# ==============================================================================
# DEPRECATED
# ==============================================================================

pttable = db.problem_tags
petable = db.problem_editorial

ptable = db.problem
ptable.truncate()

problem_tags = db(pttable).select()
problem_editorials = db(petable).select()

link_to_id = {}

for problem in problem_tags:
    print "Inserting " + problem.problem_name
    row_id = ptable.insert(name=problem.problem_name,
                           link=problem.problem_link,
                           tags=problem.tags,
                           tags_added_on=problem.problem_added_on)
    link_to_id[problem.problem_link] = row_id

db.commit()

for problem in problem_editorials:
    row = ptable(link_to_id[problem.problem_link])
    print "Updating " + row.name
    row.update_record(editorial_link=problem.editorial_link,
                      editorial_added_on=problem.problem_added_on)
