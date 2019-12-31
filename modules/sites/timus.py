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
    site_name = "Timus"

    # -------------------------------------------------------------------------
    def __init__(self, handle=""):
        """
            @param handle (String): Spoj handle
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
        response = get_request(problem_link)
        if response in REQUEST_FAILURES:
            return ["-"]

        soup = BeautifulSoup(response.text, "lxml")
        div = soup.find("div", class_="problem_links").previous_sibling
        all_as = div.find_all("a")[:-1]
        if len(all_as):
            return [x.text for x in all_as]
        else:
            return ["-"]

    # -------------------------------------------------------------------------
    @staticmethod
    def is_invalid_handle(handle):
        # Practically it is not possible for a user to enter a userID and it being
        # registered to the same user after registering on StopStalk

        """
            # @ToDo: Test the below code and handle the invalids
            url = current.SITES["Timus"] + "status.aspx?author=" + handle
            response = get_request(url)
            if response in (SERVER_FAILURE, OTHER_FAILURE):
                return True

            soup = bs4.BeautifulSoup(response.text, "lxml")
            if soup.find("p", class_="status_filter") is None:
                return True

            return False
        """

        return True

    # -------------------------------------------------------------------------
    def get_submissions(self, last_retrieved, is_daily_retrieval):
        """
            Retrieve Timus submissions after last retrieved timestamp

            @param last_retrieved (DateTime): Last retrieved timestamp for the user
            @param is_daily_retrieval (Boolean): If this call is from daily retrieval cron

            @return (Dict): Dictionary of submissions containing all the
                            information about the submissions
        """

        timus_id = self.handle
        acm_link = current.SITES["Timus"]
        submissions = []
        from_id = None
        count = 1000
        for i in xrange(1000):
            initial_url = acm_link + "status.aspx?author=" + timus_id + "&count=" + str(count)
            if from_id is None:
                url = initial_url
            else:
                url = initial_url + "&from=" + str(from_id)

            response = get_request(url, is_daily_retrieval=is_daily_retrieval)
            if response in REQUEST_FAILURES:
                return response

            soup = bs4.BeautifulSoup(response.text, "lxml")
            if soup.find("p", class_="status_filter") is None:
                return NOT_FOUND

            table = soup.find("table", class_="status")
            all_trs = table.find_all("tr")
            trs = all_trs[2:-2]

            for tr in trs:
                tds = tr.find_all("td")
                from_id = int(tds[0].text)
                curr, _, date = tds[1].contents
                curr = time.strptime(curr.text + " " + date.text, "%H:%M:%S %d %b %Y")
                curr = time.strptime(str(datetime.datetime(curr.tm_year,
                                                           curr.tm_mon,
                                                           curr.tm_mday,
                                                           curr.tm_hour,
                                                           curr.tm_min,
                                                           curr.tm_sec) + \
                                                           datetime.timedelta(minutes=30)),
                                     "%Y-%m-%d %H:%M:%S")
                if curr <= last_retrieved:
                    return submissions

                problem_link = acm_link + tds[3].contents[0]["href"] + "&locale=en"
                problem_name = tds[3].text
                language = tds[4].text
                status = tds[5].text
                submission_status = None
                if status == "Accepted":
                    submission_status = "AC"
                elif status == "Wrong answer":
                    submission_status = "WA"
                elif status.__contains__("Runtime error"):
                    submission_status = "RE"
                elif status == "Memory limit exceeded":
                    submission_status = "MLE"
                elif status == "Time limit exceeded":
                    submission_status = "TLE"
                elif status == "Compilation error":
                    submission_status = "CE"
                else:
                    submission_status = "OTH"

                if submission_status == "AC":
                    points = "100"
                else:
                    points = "0"

                submissions.append((str(time.strftime("%Y-%m-%d %H:%M:%S", curr)),
                                    problem_link,
                                    problem_name,
                                    submission_status,
                                    points,
                                    language,
                                    ""))
                from_id -= 1

            if len(trs) < count:
                break

        return submissions

# =============================================================================
