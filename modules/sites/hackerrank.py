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

        self.site = "HackerRank"
        self.handle = handle

    # -------------------------------------------------------------------------
    @staticmethod
    def get_tags(problem_link):

        if problem_link.__contains__("/contests/"):
            # If the problem_link is a contest URL
            url = problem_link.replace("https://www.hackerrank.com", "")
            url = "https://www.hackerrank.com/rest/" + url
        else:
            # Practice problem URL
            slug = problem_link.split("/")[-1]
            url = "https://www.hackerrank.com/rest/contests/master/challenges/" + slug

        response = get_request(url)
        if response == {} or response == -1:
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
    def get_submissions(self, last_retrieved):

        if self.handle:
            handle = self.handle
        else:
            return -1

        url = "https://www.hackerrank.com/rest/hackers/" + \
              handle + \
              "/recent_challenges?offset=0&limit=50000"

        tmp = get_request(url)
        if tmp == {} or tmp == -1:
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
            time_stamp = row["created_at"][:-5].split("T")
            curr = time.strptime(time_stamp[0] + " " + time_stamp[1],
                                 "%Y-%m-%d %H:%M:%S")
            if curr <= last_retrieved:
                return submissions
            append(" ".join(time_stamp))

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
