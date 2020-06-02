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
    site_name = "AtCoder"

    # -------------------------------------------------------------------------
    def __init__(self, handle=""):
        """
            @param handle (String): AtCoder handle
        """

        self.site = Profile.site_name
        self.handle = handle

    # -------------------------------------------------------------------------
    @staticmethod
    def is_valid_url(url):
        return url.__contains__("kenkoooo.com/") or \
               url.__contains__("atcoder.jp/")

    # -------------------------------------------------------------------------
    @staticmethod
    def is_website_down():
        """
            @return (Boolean): If the website is down
        """
        return (Profile.site_name in current.REDIS_CLIENT.smembers("disabled_retrieval"))

    # -------------------------------------------------------------------------
    @staticmethod
    def download_submission(view_link):
        if Profile.is_website_down():
            return -1

        response = get_request(view_link)
        if response in REQUEST_FAILURES:
            return -1

        try:
            return BeautifulSoup(response.text, "lxml").find(id="submission-code").text
        except:
            return -1

    # -------------------------------------------------------------------------
    @staticmethod
    def get_problem_setters():
        """
            @return (None): None
        """
        return None

    # -------------------------------------------------------------------------
    @staticmethod
    def get_editorial_link(problem_link):
        """
            @param problem_link (String): Problem URL

            @return (String/None): Editorial link
        """
        try:
            contest_id = re.search("contests/.*/tasks",
                                   problem_link).group().split("/")[1]
        except:
            return None

        return "https://img.atcoder.jp/%s/editorial.pdf" % contest_id

    # -------------------------------------------------------------------------
    @staticmethod
    def get_tags():
        return []

    # -------------------------------------------------------------------------
    @staticmethod
    def get_problem_details(**args):
        """
            Get problem_details given a problem link

            @param args (Dict): Dict containing problem_link
            @return (Dict): Details of the problem returned in a dictionary
        """

        return dict(tags=Profile.get_tags(),
                    editorial_link=Profile.get_editorial_link(args["problem_link"]),
                    problem_setters=Profile.get_problem_setters())

    # -------------------------------------------------------------------------
    @staticmethod
    def is_invalid_handle(handle, just_boolean=True):
        url = current.SITES["AtCoder"] + "users/" + handle
        first_response = get_request(url,
                                     timeout=10)

        if just_boolean:
            return first_response in REQUEST_FAILURES
        else:
            if first_response in REQUEST_FAILURES:
                if first_response == NOT_FOUND:
                    return True
                return first_response

            soup = BeautifulSoup(first_response.text, "lxml")
            if soup.find(class_="username").text != handle:
                return True

            return False

    # -------------------------------------------------------------------------
    @staticmethod
    def rating_graph_data(handle):
        url = "%susers/%s/history" % (current.SITES["AtCoder"], handle)

        response = get_request(url)
        if response in REQUEST_FAILURES:
            return response

        soup = bs4.BeautifulSoup(response.text, "lxml")
        try:
            trs =  soup.find("table", id="history").find("tbody").find_all("tr")
        except AttributeError:
            return []

        contest_data = {}

        for tr in trs:
            tds = tr.find_all("td")
            time_stamp = datetime.datetime.strptime(tds[0].text.split("+")[0],
                                                    "%Y-%m-%d %H:%M:%S") - \
                         datetime.timedelta(minutes=210)
            contest_data[str(time_stamp)] = {
                "name": tds[1].text.strip(),
                "url": current.SITES["AtCoder"] + \
                       tds[1].find("a",
                                   href=True)["href"][1:],
                "rating": str(tds[4].text.strip()),
                "ratingChange": str(tds[5].text),
                "rank": tds[2].text.strip()
            }

        return [{"title": "AtCoder",
                 "data": contest_data}]

    # -------------------------------------------------------------------------
    def get_submissions(self, last_retrieved,
                        atcoder_problem_dict, is_daily_retrieval):
        """
            Retrieve AtCoder submissions after last retrieved timestamp

            @param last_retrieved (DateTime): Last retrieved timestamp for the user
            @param atcoder_problem_dict (Dict): Problem ID to name mapping
            @param is_daily_retrieval (Boolean): If the retrieval is daily retrieval

            @return (List): List of submissions containing all the
                            information
        """

        self.is_daily_retrieval = is_daily_retrieval
        str_init_time = time.strptime(str(current.INITIAL_DATE),
                                      "%Y-%m-%d %H:%M:%S")
        # Test for invalid handles
        if  last_retrieved == str_init_time:
            response = Profile.is_invalid_handle(self.handle, False)
            if response == True:
                return NOT_FOUND
            elif response in REQUEST_FAILURES:
                return response

        url = "https://kenkoooo.com/atcoder/atcoder-api/results?user=" + self.handle
        response = get_request(url, is_daily_retrieval=self.is_daily_retrieval)

        if response in REQUEST_FAILURES:
            return response

        response = response.json()
        self.submissions_list = []
        submissions = sorted(response,
                             key=lambda x: x["epoch_second"],
                             reverse=True)

        for submission in submissions:
            curr = time.gmtime(submission["epoch_second"] + 330 * 60)

            if curr <= last_retrieved:
                return self.submissions_list

            try:
                problem_name = atcoder_problem_dict[submission["problem_id"]]
            except:
                return SERVER_FAILURE

            problem_link = "%scontests/%s/tasks/%s" % (current.SITES["AtCoder"],
                                                       submission["contest_id"],
                                                       submission["problem_id"])

            view_link = "%scontests/%s/submissions/%s" % (current.SITES["AtCoder"],
                                                          submission["contest_id"],
                                                          submission["id"])

            status = submission["result"]
            if status not in ["AC", "WA", "TLE", "MLE", "CE", "RE"]:
                status = "OTH"

            self.submissions_list.append((
                str(time.strftime("%Y-%m-%d %H:%M:%S", curr)),
                problem_link,
                problem_name,
                status,
                submission["point"],
                submission["language"],
                view_link
            ))

        return self.submissions_list

# =============================================================================
