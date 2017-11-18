"""
    Copyright (c) 2015-2017 Raj Patel(raj454raj@gmail.com), StopStalk

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
        uvadb = current.uvadb
        uitable = uvadb.usernametoid
        row = uvadb(uitable.username == handle).select(uitable.uva_id).first()
        if row:
            uva_id = str(row.uva_id)
        else:
            url = "http://uhunt.felix-halim.net/api/uname2uid/" + handle
            response = get_request(url)

            if response in (SERVER_FAILURE, OTHER_FAILURE):
                return response
            if response.text.strip() == "0":
                return NOT_FOUND
            uva_id = response.text

        url = "http://uhunt.felix-halim.net/api/subs-user/" + uva_id
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
        submissions = []
        all_submissions = response.json()["subs"]

        problem_url_prefix = "https://uva.onlinejudge.org/index.php?option=com_onlinejudge&Itemid=8&page=show_problem&problem="

        for row in all_submissions:
            try:
                problem_name = uvaproblems[row[1]]
            except KeyError:
                print "Problem name not found in uva problem list: " + str(row[1])
                continue
            curr_date_timestamp = str(datetime.datetime.fromtimestamp(row[4]))
            curr = time.strptime(curr_date_timestamp, "%Y-%m-%d %H:%M:%S")
            if curr <= last_retrieved:
                continue

            # Problem status
            status = row[2]
            if submission_statuses.has_key(status):
                submission_status = submission_statuses[status]
            else:
                submission_status = "OTH"

            # Points
            if submission_status == "AC":
                points = "100"
            else:
                points = "0"

            if row[5] not in languages:
                print "****************** Language: " + str(row[5]) + " not found ******************"
                continue

            submissions.append((curr_date_timestamp,
                                problem_url_prefix + str(row[1]),
                                problem_name,
                                submission_status,
                                points,
                                languages[row[5]],
                                ""))

        return submissions

# =============================================================================
