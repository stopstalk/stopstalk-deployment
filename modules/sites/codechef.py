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
from urllib import urlencode

PARAMS = {"page": 0,
          "sort_by": "All",
          "sorting_order": "asc",
          "language": "All",
          "status": "All",
          "pcode": "",
          "ccode": "",
          "Submit": "GO"}

class Profile(object):
    """
        Class containing methods for retrieving
        submissions of user
    """

    # -------------------------------------------------------------------------
    def __init__(self, handle=""):
        """
            @param handle (String): Codechef Handle
        """

        self.site = "CodeChef"
        self.handle = handle
        self.submissions = {handle: {}}
        self.retrieve_failed = False
        # Used to store the error message in case
        # of failed requests (40x/50x)
        self.retrieve_status = None

    # -------------------------------------------------------------------------
    @staticmethod
    def parsetime(time_str):
        """
            Try to parse any generalised time to
            standard format.
            For now used by Codechef

            @param time_str (String): Time in string format
                @examples: 01:59 PM 05/06/16
                           2 min ago
                           4 hours ago

            @return (DateTime): DateTime object representing the same timestamp
        """

        try:
            dt = datetime.datetime.strptime(time_str, "%I:%M %p %d/%m/%y")
            return dt
        except ValueError:
            cal = pdt.Calendar()
            dt, flags = cal.parseDT(time_str)
            assert flags
            return dt

    # -------------------------------------------------------------------------
    @staticmethod
    def get_tags(problem_link):
        """
            Get tags given a problem link

            @param problem_link (String): Problem URL
            @return (List): List of tags for the Problem
        """

        url = problem_link.split("/")
        url = url[2:]
        url.insert(1, "api/contests")
        if len(url) == 4:
            url.insert(2, "PRACTICE")
        url = "https://" + "/".join(url)

        response = get_request(url)
        if response in REQUEST_FAILURES:
            # @ToDo: Need to blacklist 404 urls also
            return ["-"]

        t = response.json()
        all_tags = []
        try:
            tags = t["tags"]
            all_as = BeautifulSoup(str(tags), "lxml").find_all("a")
            for i in all_as:
                all_tags.append(i.contents[0].strip())
            return all_tags
        except KeyError:
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
        response = get_request(problem_link)
        if response in REQUEST_FAILURES:
            return None

        soup = BeautifulSoup(response.text, "lxml")
        all_as = soup.find_all("a")

        for link in all_as:
            try:
                url = link.contents[0]
            except IndexError:
                continue
            if url.__contains__("discuss.codechef.com"):
                editorial_link = url
                break

        return editorial_link

    # -------------------------------------------------------------------------
    def process_trs(self, year, page, trs):
        """
            Process all the trs from the /submissions page of CodeChef

            @param year (Number): year
            @param page (Number): Pagination number
            @param trs (List): List of trs from the corresponding page
        """

        it = 1
        handle = self.handle
        for tr in trs:
            self.submissions[handle]["%d_%d" % (year, page)][it] = []
            submission = self.submissions[handle]["%d_%d" % (year, page)][it]
            it += 1
            append = submission.append

            all_tds = tr.find_all("td")
            if len(all_tds) == 1:
                # No recent activity
                continue

            # Time of Submission
            try:
                time_stamp = self.parsetime(all_tds[1].contents[0])
            except AttributeError:
                continue

            curr = time.strptime(str(time_stamp), "%Y-%m-%d %H:%M:%S")
            # So cool optimization!
            if curr <= self.last_retrieved:
                return "DONE"

            # Do not retrieve any further because this leads to ambiguity
            # If 2 hours ago => 2 hours 20 mins or 2 hours 14 mins ...
            # Let the user come back later when the datetime is exact
            # This prevents from redundant addition into database
            # @ToDo: For now we are allowing redundant submissions
            #        for codechef :/ . Find a way to change it.
            #if str(time_stamp).__contains__("hours"):
            #   continue
            append(str(time_stamp))

            # Problem name/URL
            problem_link = "https://www.codechef.com" + \
                            all_tds[3].contents[0]["href"]
            append(problem_link)
            try:
                problem_name = all_tds[3].contents[0].contents[0]
            except:
                print all_tds
                continue
            append(problem_name)

            # Submission status
            status_span = all_tds[5].find("span")
            status = ""
            if status_span["title"] == "":
                status = status_span.text
            else:
                status = status_span["title"]

            submission_status = "AC"
            points = "0"
            if status.__contains__("pts"):
                submission_status = "AC"
                points = status
                if float(re.sub("\[.*?\]", "", status)) < 100:
                    submission_status = "PS"
            elif status == "accepted":
                points = "100"
                submission_status = "AC"
            elif status == "wrong answer":
                submission_status = "WA"
            elif status == "compilation error":
                submission_status = "CE"
            elif status.__contains__("runtime"):
                submission_status = "RE"
            elif status == "time limit exceeded":
                submission_status = "TLE"
            else:
                submission_status = "OTH"
            append(submission_status)

            # Submission points
            append(points)

            # Submission language
            language = all_tds[8].contents[0]
            append(language)

            # View link
            view_link = "https://www.codechef.com/viewsolution/" + all_tds[0].contents[0]
            append(view_link)

    # -------------------------------------------------------------------------
    def process_page(self, year, page, url):
        """
            Process a particular submissions page

            @param year (Number): year
            @param page (Number): Pagination number
            @param url (String): url of the page to be processed
        """
        if self.retrieve_failed:
            # Note: Any thread can fail
            return

        response = get_request(url, headers={"User-Agent": user_agent})
        if response in REQUEST_FAILURES:
            self.retrieve_failed = True
            self.retrieve_status = response
            return

        soup = bs4.BeautifulSoup(response.text, "lxml")
        trs = soup.find("div", class_="tablebox").find("tbody").find_all("tr")
        self.process_trs(year, page, trs)

    # -------------------------------------------------------------------------
    def process_parallely(self, year, last_page):
        """
            Process various pages of a particular year parallely

            @param year (Number): year
            @param last_page (Number): Last page number
        """

        threads = []
        params = dict(PARAMS)
        params["year"] = year
        for page in xrange(1, last_page):
            params["page"] = page
            self.submissions[self.handle]["%d_%d" % (year, page)] = {}
            url = "https://www.codechef.com/submissions?" + urlencode(params)
            threads.append(gevent.spawn(self.process_page, year, page, url))

        gevent.joinall(threads)

    # -------------------------------------------------------------------------
    def get_submissions(self, last_retrieved):
        """
            Retrieve CodeChef submissions after last retrieved timestamp

            @param last_retrieved (DateTime): Last retrieved timestamp for the user
            @return (Dict): Dictionary of submissions containing all the
                            information about the submissions
        """

        handle = self.handle
        self.last_retrieved = last_retrieved
        PARAMS["handle"] = handle
        start_year = int(current.INITIAL_DATE.split("-")[0])
        current_year = datetime.datetime.now().year

        # To identify invalid handles
        total_retrieved = 0

        for year in xrange(current_year, start_year - 1, -1):
            # Years processed in the reverse order to break out when
            # last_retrieved time_stamp is matched
            params = dict(PARAMS)
            params["year"] = year
            url = "https://www.codechef.com/submissions?" + urlencode(params)
            response = get_request(url,
                                   headers={"User-Agent": user_agent})
            if response in REQUEST_FAILURES:
                return response

            if self.retrieve_failed:
                # One of the threads failed from the previous iteration (year)
                return self.retrieve_status

            soup = bs4.BeautifulSoup(response.text, "lxml")
            trs = soup.find("div",
                            class_="tablebox").find("tbody").find_all("tr")

            year_index = "%d_%d" % (year, 0)
            self.submissions[handle][year_index] = {}
            ret = self.process_trs(year, 0, trs)
            total_retrieved += len(self.submissions[handle][year_index][1])

            if ret == "DONE":
                return self.submissions

            pagination = soup.find("div", class_="pageinfo")
            if pagination:
                last_page = pagination.contents[0].split(" of ")[1]
                self.process_parallely(year, int(last_page))

        if total_retrieved == 0:
            # User not found
            # Note: This will include users who haven't made any submission
            #       at all on CodeChef
            return NOT_FOUND
        else:
            return self.submissions

# =============================================================================
