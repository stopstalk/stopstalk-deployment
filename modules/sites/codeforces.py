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

from .init import *

class Profile(object):
    """
        Class containing methods for retrieving
        submissions of user
    """
    site_name = "CodeForces"

    # --------------------------------------------------------------------------
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
    def get_tags(problem_link):
        """
            Get the tags of a particular problem from its URL

            @param problem_link (String): Problem URL
            @return (List): List of tags for that problem
        """

        if problem_link.__contains__("gymProblem"):
            return ["-"]

        response = get_request(problem_link)
        if response in REQUEST_FAILURES:
            return ["-"]

        tags = BeautifulSoup(response.text, "lxml").find_all("span",
                                                             class_="tag-box")

        return map(lambda tag: tag.contents[0].strip(), tags)

    # -------------------------------------------------------------------------
    @staticmethod
    def get_editorial_link(problem_link):
        """
            Get editorial link given a problem link

            @param problem_link (String): Problem URL
            @return (String/None): Editorial URL
        """
        if problem_link.__contains__("gymProblem"):
            return None

        editorial_link = None
        response = get_request(problem_link)
        if response in REQUEST_FAILURES:
            return None

        soup = BeautifulSoup(response.text, "lxml")
        all_as = soup.find_all("a")

        for link in all_as:
            url = link.contents[0]
            if url.__contains__("Tutorial"):
                # Some problems have complete url -_-
                # Example: http://codeforces.com/problemset/problem/358/C
                if link["href"][0] == "/":
                    editorial_link = "http://www.codeforces.com" + link["href"]
                else:
                    editorial_link = link["href"]
                break

        return editorial_link

    # -------------------------------------------------------------------------
    @staticmethod
    def is_invalid_handle(handle):
        response = get_request("http://www.codeforces.com/api/user.status?handle=" + \
                               handle + "&from=1&count=2")
        if response in REQUEST_FAILURES:
            return True
        return False

    # -------------------------------------------------------------------------
    @staticmethod
    def download_submission(view_link):
        if Profile.is_website_down():
            return -1

        response = get_request(view_link)
        if response in REQUEST_FAILURES:
            return -1

        try:
            return BeautifulSoup(response.text, "lxml").find("pre").text
        except:
            return -1

    # -------------------------------------------------------------------------
    @staticmethod
    def rating_graph_data(handle):
        website = "http://www.codeforces.com/"

        url = "%sapi/contest.list" % website
        response = get_request(url)
        if response in REQUEST_FAILURES:
            return response

        contest_list = response.json()["result"]
        all_contests = {}

        for contest in contest_list:
            all_contests[contest["id"]] = contest

        url = "%scontests/with/%s" % (website, handle)
        response = get_request(url)
        if response in REQUEST_FAILURES:
            return response

        soup = BeautifulSoup(response.text, "lxml")
        try:
            tbody = soup.find("table", class_="tablesorter").find("tbody")
        except AttributeError:
            print "AttributeError for Codeforces handle: " + handle
            return SERVER_FAILURE

        contest_data = {}
        for tr in tbody.find_all("tr"):
            all_tds = tr.find_all("td")
            contest_id = int(all_tds[1].find("a")["href"].split("/")[-1])
            if all_tds[2].find("a"):
                # For some users there is no rank for some contests
                # Example http://codeforces.com/contests/with/cjoa (Contest number 3)
                rank = int(all_tds[2].find("a").contents[0].strip())
            else:
                # @Todo: Will this create any issues as rank is assumed to be an int
                rank = ""
            solved_count = int(all_tds[3].find("a").contents[0].strip())
            rating_change = int(all_tds[4].find("span").contents[0].strip())
            new_rating = int(all_tds[5].contents[0].strip())
            contest = all_contests[contest_id]
            time_stamp = str(datetime.datetime.fromtimestamp(contest["startTimeSeconds"]))
            contest_data[time_stamp] = {"name": contest["name"],
                                        "url": "%scontest/%d" % (website,
                                                                 contest_id),
                                        "rating": str(new_rating),
                                        "ratingChange": rating_change,
                                        "rank": rank,
                                        "solvedCount": solved_count}

        return [{"title": "Codeforces",
                 "data": contest_data}]

    # -------------------------------------------------------------------------
    def get_submissions(self, last_retrieved, is_daily_retrieval):
        """
            Retrieve CodeForces submissions after last retrieved timestamp

            @param last_retrieved (DateTime): Last retrieved timestamp for the user
            @param is_daily_retrieval (Boolean): If this call is from daily retrieval cron

            @return (Dict): Dictionary of submissions containing all the
                            information about the submissions
        """

        handle = self.handle
        url = "http://www.codeforces.com/api/user.status?handle=" + \
              handle + "&from=1"
        # Timeout for new user submission retrieval
        timeout = 50
        if time.strftime("%Y-%m-%d %H:%M:%S", last_retrieved) != current.INITIAL_DATE:
            # Daily retrieval script to limit submissions to 500
            # A daily submitter of more than 500 submissions is really
            # supposed to contact us to prove he/she is a human :p
            url += "&count=500"
            timeout = 10
        else:
            url += "&count=50000"

        tmp = get_request(url,
                          headers={"User-Agent": user_agent},
                          timeout=timeout,
                          is_daily_retrieval=is_daily_retrieval)

        if tmp in REQUEST_FAILURES:
            return tmp

        # This was not supposed to be done here but optimization :p
        db = current.db
        ptable = db.problem
        today = datetime.datetime.now().strftime("%Y-%m-%d")

        submissions = []
        all_submissions = tmp.json()
        if all_submissions["status"] != "OK":
            return submissions
        all_submissions = all_submissions["result"]

        for row in all_submissions:

            curr = time.gmtime(row["creationTimeSeconds"] + 330 * 60)
            if curr <= last_retrieved:
                return submissions

            if row.has_key("contestId") == False:
                print "Contest ID not found for", row["problem"]["name"]
                continue

            arg = "problem/"
            if int(row["contestId"]) > 90000:
                arg = "gymProblem/"

            # Problem Name/URL
            problem_link = "http://www.codeforces.com/problemset/" + arg + \
                           str(row["contestId"]) + "/" + \
                           row["problem"]["index"]

            problem_name = row["problem"]["name"]

            # Problem status
            try:
                status = row["verdict"]
            except KeyError:
                status = "OTHER"
            submission_status = "AC"
            if status == "OK":
                submission_status = "AC"
            elif status == "WRONG_ANSWER":
                submission_status = "WA"
            elif status == "COMPILATION_ERROR":
                submission_status = "CE"
            elif status == "SKIPPED":
                submission_status = "SK"
            elif status == "RUNTIME_ERROR":
                submission_status = "RE"
            elif status == "TIME_LIMIT_EXCEEDED":
                submission_status = "TLE"
            elif status == "CHALLENGED":
                submission_status = "HCK"
            elif status == "MEMORY_LIMIT_EXCEEDED":
                submission_status = "MLE"
            else:
                submission_status = "OTH"

            # Points
            if submission_status == "AC":
                points = "100"
            elif submission_status == "HCK":
                points = "-50"
            else:
                points = "0"

            # View code link
            if problem_link.__contains__("gymProblem"):
                view_link = ""
            else:
                view_link = "http://www.codeforces.com/contest/" + \
                            str(row["contestId"]) + \
                            "/submission/" + \
                            str(row["id"])

            submissions.append((str(time.strftime("%Y-%m-%d %H:%M:%S", curr)),
                                problem_link,
                                problem_name,
                                submission_status,
                                points,
                                row["programmingLanguage"],
                                view_link))

        return submissions

# =============================================================================
