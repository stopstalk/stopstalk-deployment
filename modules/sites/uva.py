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

from .init import *

class Profile(object):
    """
        Class containing methods for retrieving
        submissions of user
    """
    site_name = "UVa"

    # -------------------------------------------------------------------------
    def __init__(self, handle=""):
        """
            @param handle (String): Codeforces Handle
        """

        self.site = Profile.site_name
        self.handle = handle

    # -------------------------------------------------------------------------
    @staticmethod
    def is_website_down():
        return (Profile.site_name in current.REDIS_CLIENT.smembers("disabled_retrieval"))

    # -------------------------------------------------------------------------
    @staticmethod
    def is_invalid_handle(handle):
        url = "http://uhunt.felix-halim.net/api/uname2uid/" + handle
        response = get_request(url)
        if response in (SERVER_FAILURE, OTHER_FAILURE) or response.text.strip() == "0":
            return True
        return False

    # -------------------------------------------------------------------------
    def get_submissions(self, last_retrieved, uva_problem_dict, is_daily_retrieval):
        """
            Retrieve UVa submissions after last retrieved timestamp

            @param last_retrieved (DateTime): Last retrieved timestamp for the user
            @param uva_problem_dict (Dict): problem_id to problem_name mapping
            @param is_daily_retrieval (Boolean): If this call is from daily retrieval cron

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
            response = get_request(url, is_daily_retrieval=is_daily_retrieval)

            if response in (SERVER_FAILURE, OTHER_FAILURE):
                return response
            if response.text.strip() == "0":
                return NOT_FOUND
            uva_id = response.text

        url = "http://uhunt.felix-halim.net/api/subs-user/" + uva_id
        response = get_request(url, is_daily_retrieval=is_daily_retrieval)
        if response in REQUEST_FAILURES:
            return response

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
                problem_name = uva_problem_dict[row[1]]
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
