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

from urllib import urlencode
from stopstalk_constants import *
from .init import *

PER_PAGE_LIMIT = 20
CODECHEF_API_URL = "https://api.codechef.com"
CODECHEF_SITE_URL = "https://www.codechef.com"
SUBMISSION_REQUEST_PARAMS = {"year": None,
                             "username": "",
                             "limit": PER_PAGE_LIMIT,
                             "offset": 0,
                             "result": "",
                             "language": "",
                             "problemCode": "",
                             "contestCode": "",
                             "fields": ""}

class Profile(object):
    """
        Class containing methods for retrieving
        submissions of user
    """
    site_name = "CodeChef"

    # --------------------------------------------------------------------------
    def __init__(self, handle=""):
        """
            @param handle (String): Codechef Handle
        """

        self.site = Profile.site_name
        self.handle = handle
        self.submissions = []
        self.access_token = None
        self.is_daily_retrieval = False
        self.last_retrieved_reached = False

    # -------------------------------------------------------------------------
    @staticmethod
    def is_valid_url(url):
        return url.__contains__("codechef.com/")

    # -------------------------------------------------------------------------
    @staticmethod
    def is_website_down():
        """
            @return (Boolean): If the website is down
        """
        return (Profile.site_name in current.REDIS_CLIENT.smembers("disabled_retrieval"))

    # --------------------------------------------------------------------------
    @staticmethod
    def get_slug(link):
        return link.split("/")[-1]

    # --------------------------------------------------------------------------
    @staticmethod
    def get_tags(response):
        """
            @param response(Dict): Response json from the API

            @return (List): List of tags
        """
        all_tags = []
        tags = utilities.get_key_from_dict(response, "tags", None)

        if tags is not None:
            all_as = BeautifulSoup(str(tags), "lxml").find_all("a")
            for i in all_as:
                all_tags.append(i.contents[0].strip())

        return all_tags

    # --------------------------------------------------------------------------
    @staticmethod
    def get_editorial_link(response):
        """
            @param response(Dict): Response json from the API

            @return (String/None): Editorial link
        """
        editorial_link = utilities.get_key_from_dict(response, "editorial_url", None)
        return None if editorial_link == "" else editorial_link

    # --------------------------------------------------------------------------
    @staticmethod
    def get_problem_setters(response):
        """
            @param response(Dict): Response json from the API

            @return (List/None): Problem authors or None
        """
        problem_author =  utilities.get_key_from_dict(response,
                                                      "problem_author",
                                                      None)
        return None if problem_author is None else [problem_author]

    # --------------------------------------------------------------------------
    @staticmethod
    def get_problem_details(**args):
        """
            Get problem_details given a problem link

            @param args (Dict): Dict containing problem_link
            @return (Dict): Details of the problem returned in a dictionary
        """
        editorial_link = None
        all_tags = []
        problem_setter = None

        api_link = args["problem_link"].replace("https://www.codechef.com/",
                                                "https://www.codechef.com/api/contests/")
        response = get_request(api_link + "?v=1554915627060",
                               headers={"User-Agent": COMMON_USER_AGENT})

        if response in REQUEST_FAILURES:
            return dict(tags=all_tags,
                        editorial_link=editorial_link,
                        problem_setters=None)

        response = response.json()

        return dict(tags=Profile.get_tags(response),
                    editorial_link=Profile.get_editorial_link(response),
                    problem_setters=Profile.get_problem_setters(response))

    # -------------------------------------------------------------------------
    @staticmethod
    def is_invalid_handle(handle):
        # CodeChef is very flaky
        return True
        response = get_request("https://www.codechef.com/users/" + handle)
        if (response in REQUEST_FAILURES) or response.url.__contains__("teams/view"):
            return True
        return False

    # -------------------------------------------------------------------------
    @staticmethod
    def download_submission(view_link):
        if Profile.is_website_down():
            return -1

        problem_id = view_link.strip("/").split("/")[-1]
        download_url = "https://www.codechef.com/viewplaintext/" + \
                       str(problem_id)
        response = get_request(download_url,
                               headers={"User-Agent": COMMON_USER_AGENT})
        if response in REQUEST_FAILURES:
            return -1
        try:
            return BeautifulSoup(response.text, "lxml").find("pre").text
        except:
            return -1

    # -------------------------------------------------------------------------
    @staticmethod
    def rating_graph_data(handle):
        url = "https://www.codechef.com/users/" + handle
        response = get_request(url, headers={"User-Agent": COMMON_USER_AGENT})

        if response in REQUEST_FAILURES:
            return response

        ratings = eval(re.search("var all_rating = .*?;", response.text).group()[17:-1].replace("null", "None"))

        long_contest_data = {}
        cookoff_contest_data = {}
        ltime_contest_data = {}

        for contest in ratings:
            this_obj = None
            if contest["code"].__contains__("COOK"):
                # Cook off contest
                this_obj = cookoff_contest_data
            elif contest["code"].__contains__("LTIME"):
                # Lunchtime contest
                this_obj = ltime_contest_data
            else:
                # Long contest
                this_obj = long_contest_data
            # getdate, getmonth and getyear give end_date only
            time_stamp = str(datetime.datetime.strptime(contest["end_date"], "%Y-%m-%d %H:%M:%S"))
            this_obj[time_stamp] = {"name": contest["name"],
                                    "url": "https://www.codechef.com/" + contest["code"],
                                    "rating": str(contest["rating"]),
                                    "rank": contest["rank"]}

        return [{"title": "CodeChef Long",
                 "data": long_contest_data},
                {"title": "CodeChef Cook-off",
                 "data": cookoff_contest_data},
                {"title": "CodeChef Lunchtime",
                 "data": ltime_contest_data}]

    # --------------------------------------------------------------------------
    def __validate_handle(self):
        """
            Make an API request to Codechef to see if a user exists
        """

        response = get_request("%s/users/%s" % (CODECHEF_API_URL, self.handle),
                               headers={"User-Agent": COMMON_USER_AGENT,
                                        "Authorization": "Bearer %s" % self.access_token},
                               timeout=10,
                               is_daily_retrieval=self.is_daily_retrieval)
        if response in REQUEST_FAILURES:
            return response

        # User was not found in Codechef database
        json_data = response.json()
        if json_data["result"]["data"]["code"] == 9003:
            return NOT_FOUND
        else:
            return "VALID_HANDLE"

    # --------------------------------------------------------------------------
    def __get_access_token(self):
        """
            Get CodeChef API access_token from the database
        """

        # Codechef has a TTL of 1 hour for every generated access token
        TTL_TIME = 60 * 60
        # We are assuming there might be cases when 1 submission retrieval takes
        # more than 10 minutes
        SAFE_TIME = 10 * 60

        redis_key = "codechef_access_token"
        redis_ttl = current.REDIS_CLIENT.ttl(redis_key)
        if redis_ttl is not None and redis_ttl > SAFE_TIME:
            return current.REDIS_CLIENT.get(redis_key)

        response = requests.post("%s/oauth/token" % CODECHEF_API_URL,
                                 data={"grant_type": "client_credentials",
                                       "scope": "public",
                                       "client_id": current.codechef_client_id,
                                       "client_secret": current.codechef_client_secret,
                                       "redirect_uri": ""})
        json_data = response.json()
        if response.status_code == 200 and json_data["status"] == "OK":
            access_token = json_data["result"]["data"]["access_token"]
            current.REDIS_CLIENT.set(redis_key,
                                     access_token,
                                     ex=TTL_TIME)
            return access_token
        else:
            print "Error requesting CodeChef API for access token"
            return

    # --------------------------------------------------------------------------
    def __get_problem_link(self, contest_code, problem_code):
        """
            Get the problem link given the contest_code and problem_code
            @params contest_code (String): Contest code of the problem
            @params problem_code (String): Problem code of the problem

            @return (String): URL of the problem
        """
        return "%s/%s/problems/%s" % (CODECHEF_SITE_URL,
                                      contest_code,
                                      problem_code)

    # --------------------------------------------------------------------------
    def __process_year_submissions(self, year, last_retrieved):
        SUBMISSION_REQUEST_PARAMS["year"] = year
        SUBMISSION_REQUEST_PARAMS["offset"] = 0
        submissions = []
        for _ in xrange(1000):
            response = get_request("%s/submissions" % CODECHEF_API_URL,
                                   headers={"Authorization": "Bearer %s" % self.access_token},
                                   params=SUBMISSION_REQUEST_PARAMS,
                                   timeout=10,
                                   is_daily_retrieval=self.is_daily_retrieval)
            if response in REQUEST_FAILURES:
                return response

            json_response = response.json()
            if json_response["result"]["data"]["code"] == 9003:
                # No submisions for the year
                return submissions

            for submission in json_response["result"]["data"]["content"]:
                curr = time.strptime(submission["date"],
                                     TIME_CONVERSION_STRING)
                if curr <= last_retrieved:
                    self.last_retrieved_reached = True
                    return submissions

                problem_link = self.__get_problem_link(submission["contestCode"],
                                                       submission["problemCode"])
                problem_name = submission["problemCode"]
                status = submission["result"]
                points = submission["score"]
                if status == "AC":
                    if float(points) > 0 and float(points) < 100:
                        status = "PS"
                elif status in ["WA", "TLE"]:
                    pass
                elif status == "CTE":
                    status = "CE"
                elif status == "RTE":
                    status = "RE"
                else:
                    print "*****************", status
                    status = "OTH"
                language = submission["language"]
                view_link = "%s/viewsolution/%d" % (CODECHEF_SITE_URL,
                                                    submission["id"])
                submissions.append((submission["date"],
                                    problem_link,
                                    problem_name,
                                    status,
                                    points,
                                    language,
                                    view_link))
            if len(json_response["result"]["data"]["content"]) < PER_PAGE_LIMIT:
                break

            SUBMISSION_REQUEST_PARAMS["offset"] += PER_PAGE_LIMIT

        return submissions

    # --------------------------------------------------------------------------
    def get_submissions(self, last_retrieved, is_daily_retrieval):
        """
            Retrieve CodeChef submissions after last retrieved timestamp

            @param last_retrieved (DateTime): Last retrieved timestamp for the user
            @param is_daily_retrieval (Boolean): If this call is from daily retrieval cron
            @return (Dict): Dictionary of submissions containing all the
                            information about the submissions
        """

        if current.environment == "development":
            # Locally client credentials for CodeChef API wouldn't be valid and
            # there is no other fallback method which can be used for retrieval
            return SERVER_FAILURE

        self.is_daily_retrieval = is_daily_retrieval
        try:
            # If the handle is a URL return NOT_FOUND
            re.match("https?://.*\.com", self.handle).group()
            return NOT_FOUND
        except AttributeError:
            pass

        start_year = last_retrieved.tm_year
        current_year = datetime.datetime.now().year
        str_init_time = time.strptime(str(current.INITIAL_DATE),
                                      "%Y-%m-%d %H:%M:%S")

        self.access_token = self.__get_access_token()
        if self.access_token is None:
            print "Access token found none"
            return SERVER_FAILURE

        # Test for invalid handles
        if  last_retrieved == str_init_time:
            response = self.__validate_handle()
            if response in REQUEST_FAILURES:
                return response

        SUBMISSION_REQUEST_PARAMS["username"] = self.handle
        self.submissions = []

        for year in xrange(current_year, start_year - 1, -1):
            # Years processed in the reverse order to break out when
            # last_retrieved time_stamp is matched

            result = self.__process_year_submissions(year, last_retrieved)
            if result in REQUEST_FAILURES:
                return result
            else:
                self.submissions.extend(result)
                if self.last_retrieved_reached:
                    return self.submissions

        return self.submissions

# =============================================================================
