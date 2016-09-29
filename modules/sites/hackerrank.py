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
            @param handle (String): HackerRank handle
        """

        self.site = "HackerRank"
        self.handle = handle

    # -------------------------------------------------------------------------
    @staticmethod
    def get_tags(problem_link):
        """
            Get the tags of a particular problem from its URL

            @param problem_link (String): Problem URL
            @return (List): List of tags for that problem
        """

        if problem_link.__contains__("/contests/"):
            # If the problem_link is a contest URL
            url = problem_link.replace("https://www.hackerrank.com", "")
            url = "https://www.hackerrank.com/rest/" + url
        else:
            # Practice problem URL
            slug = problem_link.split("/")[-1]
            url = "https://www.hackerrank.com/rest/contests/master/challenges/" + slug

        response = get_request(url)
        if response in REQUEST_FAILURES:
            return ["-"]

        response = response.json()

        track = response["model"]["track"]
        primary_contest = response["model"]["primary_contest"]
        all_tags = ["-"]
        if track:
            # If the problem is a practice problem
            all_tags = [track["name"]]
        elif primary_contest["track"]:
            # If the problem is a contest problem with track
            all_tags = [primary_contest["track"]["name"]]
        elif primary_contest["name"]:
            # If the problem is a contest problem without track
            # Then consider contest name as tag
            all_tags = [primary_contest["name"]]

        return all_tags

    # -------------------------------------------------------------------------
    @staticmethod
    def get_editorial_link(problem_link):
        """
            Get editorial link given a problem link

            @param problem_link (String): Problem URL
            @return (String/None): Editorial URL
        """
        editorial_link = None
        if problem_link.__contains__("contests"):
            rest_url = problem_link.replace("contests/",
                                            "rest/contests/")
        else:
            rest_url = problem_link.replace("challenges/",
                                            "rest/contests/master/challenges/")
        response = get_request(rest_url)
        if response in REQUEST_FAILURES:
            return editorial_link

        editorial_present = response.json()["model"]["is_editorial_available"]
        return problem_link + "/editorial/" if editorial_present else None

    # -------------------------------------------------------------------------
    def get_submissions(self, last_retrieved):
        """
            Retrieve HackerRank submissions after last retrieved timestamp

            @param last_retrieved (DateTime): Last retrieved timestamp for the user
            @return (Dict): Dictionary of submissions containing all the
                            information about the submissions
        """

        handle = self.handle
        url = "https://www.hackerrank.com/rest/hackers/" + \
              handle + \
              "/recent_challenges?offset=0&limit=50000"

        tmp = get_request(url)
        if tmp in REQUEST_FAILURES:
            return tmp

        all_submissions = tmp.json()["models"]

        submissions = {handle: {1 : {}}}
        it = 0
        for row in all_submissions:

            submission = submissions[handle][1]
            submission[it] = []
            submission = submission[it]
            append = submission.append

            # Time of submission
            # @Todo: This is ugly
            time_stamp = row["created_at"][:-5].split("T")
            time_stamp = time.strptime(time_stamp[0] + " " + time_stamp[1],
                                       "%Y-%m-%d %H:%M:%S")
            time_stamp = datetime.datetime(time_stamp.tm_year,
                                           time_stamp.tm_mon,
                                           time_stamp.tm_mday,
                                           time_stamp.tm_hour,
                                           time_stamp.tm_min,
                                           time_stamp.tm_sec) + \
                                           datetime.timedelta(minutes=330)
            curr = time.strptime(str(time_stamp), "%Y-%m-%d %H:%M:%S")

            if curr <= last_retrieved:
                return submissions
            append(str(time_stamp))

            # Problem link
            append("https://www.hackerrank.com" + row["url"])

            # Problem name
            append(row["name"])

            # Status
            # HackerRank only gives the list of solved problems
            append("AC")

            # Points
            append("100")

            # Language
            append("-")

            # View code link
            append("")

            it += 1

        return submissions

# =============================================================================
