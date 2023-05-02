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
    def is_valid_url(url):
        return url.__contains__("codeforces.com/")

    # -------------------------------------------------------------------------
    @staticmethod
    def is_website_down():
        """
            @return (Boolean): If the website is down
        """
        return (Profile.site_name in current.REDIS_CLIENT.smembers("disabled_retrieval"))

    # -------------------------------------------------------------------------
    @staticmethod
    def get_contest_id(problem_link):
        """
            Get contest ID from a problem_link

            @param problem_link (String): Problem URL
            @return (Integer): Contest ID from the URL
        """
        return problem_link.split("/")[-2]

    # -------------------------------------------------------------------------
    @staticmethod
    def get_url_parts(problem_link=None, parts=None):
        if parts is None:
            parts = problem_link.split("/")[-2:]

        return "problem_" + "_".join(parts)

    # -------------------------------------------------------------------------
    @staticmethod
    def make_codeforces_request(url):
        return get_request(url,
                           headers=current.codeforces_headers,
                           cookies=current.codeforces_cookies)

    # -------------------------------------------------------------------------
    @staticmethod
    def get_editorial_link(problem_link):
        """
            @param problem_link(String): Problem link of the page

            @return (String/None): Editorial link
        """
        editorial_link = None
        response = Profile.make_codeforces_request(problem_link)
        if response in REQUEST_FAILURES:
            return editorial_link

        soup = BeautifulSoup(response.text, "lxml")
        all_as = soup.find_all("a")
        for link in all_as:
            if len(link.contents) == 0:
                continue
            url = link.contents[0]
            if url.__contains__("Tutorial"):
                # Some problems have complete url -_-
                # Example: http://codeforces.com/problemset/problem/358/C
                if link["href"][0] == "/":
                    editorial_link = "http://codeforces.com" + link["href"]
                else:
                    editorial_link = link["href"]
                break

        return editorial_link

    # -------------------------------------------------------------------------
    @staticmethod
    def get_tags(problem_link):
        """
            @param problem_link(String): Problem link of the page

            @return (List): List of tags
        """

        value = current.REDIS_CLIENT.hgetall("codeforces_problem_tag_mapping")
        if len(value) == 0:
            response = get_request("https://codeforces.com/api/problemset.problems")
            if response in REQUEST_FAILURES:
                return []

            result = response.json()["result"]["problems"]
            redis_dict = {}
            for problem in result:
                redis_key = Profile.get_url_parts(parts=[str(problem["contestId"]),
                                                         problem["index"]])
                redis_dict[redis_key] = problem["tags"]

            current.REDIS_CLIENT.hmset("codeforces_problem_tag_mapping",
                                       redis_dict)

            value = redis_dict

        redis_key = Profile.get_url_parts(problem_link=problem_link)
        if redis_key in value:
            from ast import literal_eval
            return literal_eval(value[redis_key])
        else:
            return []

    # -------------------------------------------------------------------------
    @staticmethod
    def get_problem_setters(problem_link):
        """
            @param problem_link(String): Problem link of the page

            @return (List/None): Problem authors or None
        """
        import json
        mappings = current.REDIS_CLIENT.get(CODEFORCES_PROBLEM_SETTERS_KEY)
        if mappings is None:
            file_path = "./applications/stopstalk/problem_setters/codeforces_metadata.json"
            try:
                file_obj = open(file_path, "r")
            except IOError:
                return None

            mappings = json.loads(file_obj.read())
            current.REDIS_CLIENT.set(CODEFORCES_PROBLEM_SETTERS_KEY,
                                     json.dumps(mappings))
            file_obj.close()

        mappings = json.loads(mappings)
        contest_id = Profile.get_contest_id(problem_link)
        if contest_id in mappings["normal"]:
            return mappings["normal"][contest_id]
        elif contest_id in mappings["gym"]:
            return mappings["gym"][contest_id]
        else:
            return None

    # -------------------------------------------------------------------------
    @staticmethod
    def get_problem_details(**args):
        """
            Get problem_details given a problem link

            @param args (Dict): Dict containing problem_link
            @return (Dict): Details of the problem returned in a dictionary
        """

        all_tags = []
        editorial_link = None
        problem_link = args["problem_link"]
        problem_setters = None
        if problem_link.__contains__("gymProblem"):
            return dict(editorial_link=editorial_link,
                        tags=all_tags,
                        problem_setters=problem_setters)

        if "problem_setters" in args["update_things"]:
            problem_setters = Profile.get_problem_setters(problem_link)

        if "editorial_link" in args["update_things"]:
            editorial_link = Profile.get_editorial_link(problem_link)

        if "tags" in args["update_things"]:
            all_tags = Profile.get_tags(problem_link)

        return dict(editorial_link=editorial_link,
                    tags=all_tags,
                    problem_setters=problem_setters)

    # -------------------------------------------------------------------------
    @staticmethod
    def is_invalid_handle(handle):
        response = get_request("http://codeforces.com/api/user.status?handle=" + \
                               handle + "&from=1&count=2")

        if response == NOT_FOUND:
            return True

        response = response.json()

        if response["status"] != "ok":
            return True
        else:
            return False

        return False

    # -------------------------------------------------------------------------
    @staticmethod
    def download_submission(view_link):
        if Profile.is_website_down():
            return -1

        response = Profile.make_codeforces_request(view_link)
        if response in REQUEST_FAILURES:
            return -1

        try:
            return BeautifulSoup(response.text, "lxml").find(id="program-source-text").text
        except:
            return -1

    # -------------------------------------------------------------------------
    @staticmethod
    def rating_graph_data(handle):
        website = "http://codeforces.com/"

        url = "%sapi/contest.list" % website
        response = get_request(url)
        if response in REQUEST_FAILURES:
            return response

        contest_list = response.json()["result"]
        all_contests = {}

        for contest in contest_list:
            all_contests[contest["id"]] = contest

        url = "%scontests/with/%s" % (website, handle)
        response = Profile.make_codeforces_request(url)

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
            rank = int(all_tds[3].text.strip())
            solved_count = int(all_tds[4].find("a").contents[0].strip())
            rating_change = int(all_tds[5].find("span").contents[0].strip())
            new_rating = int(all_tds[6].contents[0].strip())
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
        url = "http://codeforces.com/api/user.status?handle=" + \
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
            if "not found" in all_submissions["comment"]:
                return NOT_FOUND
            else:
                return SERVER_FAILURE
        all_submissions = all_submissions["result"]

        for row in all_submissions:

            curr = time.gmtime(row["creationTimeSeconds"] + 330 * 60)
            if curr <= last_retrieved:
                return submissions

            if row.has_key("contestId") == False:
                try:
                    problem_link = "http://codeforces.com/problemsets/" + \
                                   row["problem"]["problemsetName"] + \
                                   "/problem/99999/" + str(row["problem"]["index"])
                except Exception as e:
                    print "Unable to create problem_link for", row
                    continue
            else:
                arg = "problem/"
                if int(row["contestId"]) > 90000:
                    arg = "gymProblem/"

                # Problem Name/URL
                problem_link = "http://codeforces.com/problemset/" + arg + \
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
            if problem_link.__contains__("gymProblem") or \
               row.has_key("contestId") == False:
                view_link = ""
            else:
                view_link = "http://codeforces.com/contest/" + \
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
