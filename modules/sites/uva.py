"""
    Copyright (c) 2015-2016 Raj Patel(raj454raj@gmail.com), StopStalk

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

from .init import *

class Profile(object):
    """
        Class containing methods for retrieving
        submissions of user
    """

    # -------------------------------------------------------------------------
    def __init__(self, handle=""):
        """
            @param handle (String): Codeforces Handle
        """

        self.site = "UVa"
        self.handle = handle

    # -------------------------------------------------------------------------
    def get_submissions(self, last_retrieved):
        """
            Retrieve UVa submissions after last retrieved timestamp

            @param last_retrieved (DateTime): Last retrieved timestamp for the user
            @return (Dict): Dictionary of submissions containing all the
                            information about the submissions
        """

        handle = self.handle
        url = "http://uhunt.felix-halim.net/api/uname2uid/" + handle
        response = get_request(url)

        if response in (SERVER_FAILURE, OTHER_FAILURE):
            return response
        if response.text == "0":
            return NOT_FOUND

        url = "http://uhunt.felix-halim.net/api/subs-user/" + response.text
        response = get_request(url)
        if response in REQUEST_FAILURES:
            return response

        uvadb = current.uvadb
        ptable = uvadb.problem
        uvaproblems = uvadb(ptable).select(ptable.problem_id, ptable.title)
        uvaproblems = dict([(x.problem_id, x.title) for x in uvaproblems])
        submission_statuses = {90: "AC",
                               70: "WA",
                               30: "CE",
                               40: "RE",
                               50: "TLE",
                               60: "MLE"}
        languages = {1: "ANSI C",
                     2: "Java",
                     3: "C++",
                     4: "Pascal",
                     5: "C++11",
                     6: "Python"}
        submissions = {handle: {1: {}}}
        all_submissions = response.json()["subs"]

        it = 0
        problem_url_prefix = "https://uva.onlinejudge.org/index.php?option=com_onlinejudge&Itemid=8&page=show_problem&problem="

        for row in all_submissions:
            submissions[handle][1][it] = []
            submission = submissions[handle][1][it]
            append = submission.append

            it += 1
            curr_date_timestamp = str(datetime.datetime.fromtimestamp(row[4]))
            curr = time.strptime(curr_date_timestamp, "%Y-%m-%d %H:%M:%S")
            if curr <= last_retrieved:
                continue

            # Time of submission
            append(curr_date_timestamp)

            # Problem URL
            append(problem_url_prefix + str(row[1]))

            # Problem Name
            append(uvaproblems[row[1]])

            # Problem status
            status = row[2]
            if submission_statuses.has_key(status):
                submission_status = submission_statuses[status]
            else:
                submission_status = "OTH"
            append(submission_status)

            # Points
            if submission_status == "AC":
                points = "100"
            else:
                points = "0"
            append(points)

            # Language
            append(languages[row[5]])

            append("")

            it += 1

        return submissions

# =============================================================================
