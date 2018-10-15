"""
    Copyright (c) 2015-2018 Raj Patel(raj454raj@gmail.com), StopStalk

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

        self.site = "CodeForces"
        self.handle = handle

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
        response = get_request("http://codeforces.com/api/user.status?handle=" + \
                               handle + "&from=1&count=2")
        if response in REQUEST_FAILURES:
            return True
        return False

    # -------------------------------------------------------------------------
    def get_submissions(self, last_retrieved, plink_to_id):
        """
            Retrieve CodeForces submissions after last retrieved timestamp

            @param last_retrieved (DateTime): Last retrieved timestamp for the user
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
                          timeout=timeout)

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

            # Problem tags
            tags = row["problem"]["tags"]
            if tags == []:
                tags = ["-"]

            if plink_to_id.has_key(problem_link):
                this_value = plink_to_id[problem_link]
                if tags != ["-"] and this_value[0] == "['-']":
                    print "Codeforces tag updated", problem_link, tags
                    db(ptable.id == this_value[1]).update(tags=str(tags))
            else:
                print "Codeforces tag inserted", problem_link, tags
                rid = ptable.insert(link=problem_link,
                                    name=problem_name,
                                    tags=str(tags),
                                    tags_added_on=today)
                plink_to_id[problem_link] = (str(tags), rid)

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
