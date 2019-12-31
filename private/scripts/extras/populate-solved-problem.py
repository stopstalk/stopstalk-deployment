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

import pickle

with open("problem_stats", "rb") as f:
    final_hash = pickle.load(f)

def build_when_string(current_problems):
    all_vars = [""] * 4
    for problem in current_problems:
        for it in xrange(4):
            if it >= 2:
                if problem[1][it] is None:
                    problem[1][it] = ""
                all_vars[it] += "WHEN '" + problem[0] + "' THEN '" + str(problem[1][it]) + "'"
            else:
                all_vars[it] += "WHEN '" + problem[0] + "' THEN " + str(problem[1][it])
            all_vars[it] += "\n"
    return all_vars

batch_size = 700

for i in xrange(0, len(final_hash), batch_size):
    current_problems = final_hash[i : i + batch_size]
    all_vars = build_when_string(current_problems)
    all_vars.append(",".join(["'" + x[0] + "'" for x in current_problems]))
    sql_query = """
                UPDATE problem
                SET solved_submissions = CASE link
                                            %s
                                            ELSE solved_submissions
                                         END,
                    total_submissions = CASE link
                                            %s
                                            ELSE total_submissions
                                        END,
                    user_ids = CASE link
                                    %s
                                    ELSE user_ids
                               END,
                    custom_user_ids = CASE link
                                        %s
                                        ELSE custom_user_ids
                                      END
                WHERE link in (%s)
                """ % tuple(all_vars)
    db.executesql(sql_query)
