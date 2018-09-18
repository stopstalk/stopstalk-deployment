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
            @param handle (String): Spoj handle
        """

        self.site = "Spoj"
        self.handle = handle

    # -------------------------------------------------------------------------
    @staticmethod
    def get_tags(problem_link):
        """
            Get the tags of a particular problem from its URL

            @param problem_link (String): Problem URL
            @return (List): List of tags for that problem
        """

        # Temporary hack - spoj seems to have removed their SSL cert
        problem_link = problem_link.replace("https", "http")
        response = get_request(problem_link)
        if response in REQUEST_FAILURES:
            return ["-"]

        tags = BeautifulSoup(response.text, "lxml").find_all("div",
                                                             id="problem-tags")
        try:
            tags = tags[0].findAll("span")
        except IndexError:
            return ["-"]
        all_tags = []

        for tag in tags:
            tmp = tag.contents
            if tmp != []:
                all_tags.append(tmp[0][1:])

        return all_tags

    # -------------------------------------------------------------------------
    def get_submissions(self, last_retrieved):
        """
            Retrieve Spoj submissions after last retrieved timestamp

            @param last_retrieved (DateTime): Last retrieved timestamp for the user
            @return (Dict): Dictionary of submissions containing all the
                            information about the submissions
        """

        handle = self.handle
        submissions = []
        start = 0

        previd = -1
        currid = 0

        str_init_time = time.strptime(str(current.INITIAL_DATE),
                                      "%Y-%m-%d %H:%M:%S")
        # Test for invalid handles
        if  last_retrieved == str_init_time:
            url = current.SITES[self.site] + "users/" + handle
            tmpreq = get_request(url, timeout=10)

            if tmpreq in REQUEST_FAILURES:
                return tmpreq

            # Bad but correct way of checking if the handle exists
            if tmpreq.text.find("History of submissions") == -1:
                return NOT_FOUND

        for i in xrange(1000):
            flag = 0
            url = current.SITES[self.site] + "status/" + \
                  handle + \
                  "/all/start=" + \
                  str(start)

            start += 20
            t = get_request(url, timeout=10)
            if t in REQUEST_FAILURES:
                return t

            soup = bs4.BeautifulSoup(t.text, "lxml")
            table_body = soup.find("tbody")

            # Check if the page retrieved has no submissions
            if len(table_body) == 1:
                return submissions

            row = 0
            for i in table_body:
                if isinstance(i, bs4.element.Tag):
                    if row == 0:
                        currid = i.contents[1].contents[0]
                        if currid == previd:
                            flag = 1
                            break
                    row += 1
                    previd = currid

                    # Time of submission
                    tos = i.contents[3].contents[1].contents[0]
                    curr = time.strptime(str(tos), "%Y-%m-%d %H:%M:%S")
                    curr = datetime.datetime(curr.tm_year,
                                             curr.tm_mon,
                                             curr.tm_mday,
                                             curr.tm_hour,
                                             curr.tm_min,
                                             curr.tm_sec) + \
                                             datetime.timedelta(minutes=210)
                    tos = str(curr)
                    curr = time.strptime(tos, "%Y-%m-%d %H:%M:%S")
                    if curr <= last_retrieved:
                        return submissions

                    # Problem Name/URL
                    uri = i.contents[5].contents[0]
                    uri["href"] = "https://www.spoj.com" + uri["href"]
                    problem_link = eval(repr(uri["href"]).replace("\\", ""))

                    # Problem Status
                    status = str(i.contents[6])
                    if status.__contains__("accepted"):
                        submission_status = "AC"
                    elif status.__contains__("wrong"):
                        submission_status = "WA"
                    elif status.__contains__("compilation"):
                        submission_status = "CE"
                    elif status.__contains__("runtime"):
                        submission_status = "RE"
                    elif status.__contains__("time limit"):
                        submission_status = "TLE"
                    else:
                        submission_status = "OTH"

                    # Question Points
                    if submission_status == "AC":
                        points = "100"
                    else:
                        points = "0"

                    submissions.append((tos,
                                        problem_link,
                                        uri.contents[0].strip(),
                                        submission_status,
                                        points,
                                        i.contents[12].contents[1].contents[0],
                                        ""))

            if flag == 1:
                break

        return submissions

# =============================================================================
