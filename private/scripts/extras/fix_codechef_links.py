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

stable = db.submission
ptable = db.problem

query = (stable.site == "CodeChef") & \
        ((stable.problem_link.contains("codechef.com/problems/")) | \
         (stable.problem_link.contains("http://www")))
for record in db(query).iterselect():
    previous_link = record.problem_link
    new_link = previous_link.replace("codechef.com/problems/", "codechef.com/PRACTICE/problems/")
    new_link = new_link.replace("http://www", "https://www")
    record.update_record(problem_link=new_link)
    print previous_link, new_link

query = (ptable.link.contains("codechef.com/") & \
         (ptable.link.contains("codechef.com/problems/") | \
          ptable.link.contains("http://www")))
for record in db(query).iterselect():
    previous_link = record.link
    new_link = previous_link.replace("codechef.com/problems/", "codechef.com/PRACTICE/problems/")
    new_link = new_link.replace("http://www", "https://www")
    record.update_record(link=new_link)
    print previous_link, new_link
