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
            @param handle (String): Codechef Handle
        """

        self.site = "CodeChef"
        self.handle = handle
        self.submissions = {handle: {}}
        self.retrieve_failed = False

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
        if response == -1 or response == {}:
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
    def parallelize_codechef(self, handle, page, last_retrieved):
        """
            Helper function for retrieving codechef submissions parallely

            @param handle (String): CodeChef handle
            @param page (Integer): Pagination page number
            @param last_retrieved (DateTime): Last retrieved for that user
        """

        if self.retrieve_failed:
            return

        url = "https://www.codechef.com/recent/user?user_handle=" + \
               handle + \
               "&page=" + \
               str(page)

        tmp = get_request(url, headers={"User-Agent": user_agent})

        # GET request failed
        if tmp == -1 or tmp == {}:
            self.retrieve_failed = True
            return

        d = ast.literal_eval(tmp.text)["content"]

        it = 1
        self.submissions[handle][page] = {}
        x = bs4.BeautifulSoup(d, "lxml")

        trs = x.find_all("tr")[1:]
        for i in trs:
            self.submissions[handle][page][it] = []
            submission = self.submissions[handle][page][it]
            append = submission.append

            try:
                # tos = time_of_submission
                tos = i.contents[0].contents[0]
            except AttributeError:
                continue
            tos = str(ast.literal_eval(repr(tos).replace("\\", "")))
            tos = self.parsetime(tos)
            curr = time.strptime(str(tos), "%Y-%m-%d %H:%M:%S")

            # So cool optimization!
            if curr <= last_retrieved:
                return

            append(str(tos))

            # Problem name/url
            prob = i.contents[1].contents[0]
            prob["href"] = "http://www.codechef.com" + prob["href"]
            problem_link = eval(repr(prob["href"]).replace("\\", ""))
            append(problem_link)
            try:
                append(prob.contents[0])
            except IndexError:
                append("")

            # Submission status
            status = i.contents[2].contents[0].find("img")["src"]
            status = repr(status).replace("\\", "")
            status = status[7:-5]
            submission_status = "AC"
            if status == "tick-icon":
                submission_status = "AC"
            elif status == "cross-icon":
                submission_status = "WA"
            elif status == "alert-icon":
                submission_status = "CE"
            elif status == "runtime-error":
                submission_status = "RE"
            elif status == "clock_error":
                submission_status = "TLE"
            else:
                submission_status = "OTH"
            append(submission_status)

            # Question points
            pts = i.contents[2].contents[0].contents
            try:
                if  len(pts) >= 5:
                    points = pts[2] + " " + pts[4]
                else:
                    points = pts[2]
            except IndexError:
                if submission_status == "AC":
                    points = "100"
                else:
                    points = "0"
            append(points)

            # Language
            append(i.contents[3].contents[0].strip())

            # View code link
            # @ToDo: Find a way to get the code link
            view_link = ""
            append(view_link)

            it += 1

    # -------------------------------------------------------------------------
    def get_submissions(self, last_retrieved):
        """
            Retrieve CodeChef submissions after last retrieved timestamp

            @param last_retrieved (DateTime): Last retrieved timestamp for the user
            @return (Dict): Dictionary of submissions containing all the
                            information about the submissions
        """

        if self.retrieve_failed:
            return -1

        if self.handle:
            handle = self.handle
        else:
            return -1

        user_url = "http://www.codechef.com/recent/user?user_handle=" + handle

        tmp = get_request(user_url, headers={"User-Agent": user_agent})

        if tmp == -1 or tmp == {}:
            return tmp

        d = ast.literal_eval(tmp.text)
        max_page = d["max_page"]
        submissions = {handle: {}}
        it = 1

        # Apply parallel processing only if retrieving from the INITIAL_DATE
        tmp_const = time.strptime(current.INITIAL_DATE, "%Y-%m-%d %H:%M:%S")
        if tmp_const == last_retrieved:
            threads = []
            for i in xrange(max_page):
                threads.append(gevent.spawn(self.parallelize_codechef,
                                            handle,
                                            i,
                                            last_retrieved))
            gevent.joinall(threads)
            return self.submissions

        else:
            for page in xrange(0, max_page):
                user_url = "http://www.codechef.com/recent/user?user_handle=" + \
                           handle + \
                           "&page=" + \
                           str(page)

                tmp = get_request(user_url, headers={"User-Agent": user_agent})

                if tmp == -1:
                    return -1

                d = ast.literal_eval(tmp.text)["content"]

                submissions[handle][page] = {}
                x = bs4.BeautifulSoup(d, "lxml")
                trs = x.find_all("tr")[1:]
                for i in trs:

                    submissions[handle][page][it] = []
                    submission = submissions[handle][page][it]
                    append = submission.append

                    try:
                        # tos = time_of_submission
                        tos = i.contents[0].contents[0]
                    except AttributeError:
                        continue
                    tos = str(ast.literal_eval(repr(tos).replace("\\", "")))

                    # Do not retrieve any further because this leads to ambiguity
                    # If 2 hours ago => 2 hours 20 mins or 2 hours 14 mins ...
                    # Let the user come back later when the datetime is exact
                    # This prevents from redundant addition into database
                    # @ToDo: For now we are allowing redundant submissions
                    #        for codechef :/ . Find a way to change it.
                    #if tos.__contains__("hours"):
                    #   continue

                    tos = self.parsetime(tos)
                    curr = time.strptime(str(tos), "%Y-%m-%d %H:%M:%S")

                    if curr <= last_retrieved:
                        return submissions
                    append(str(tos))

                    # Problem name/url
                    prob = i.contents[1].contents[0]
                    prob["href"] = "http://www.codechef.com" + prob["href"]
                    problem_link = eval(repr(prob["href"]).replace("\\", ""))
                    append(problem_link)
                    try:
                        append(prob.contents[0])
                    except IndexError:
                        append("")

                    # Submission status
                    status = i.contents[2].contents[0].find("img")["src"]
                    status = repr(status).replace("\\", "")
                    status = status[7:-5]
                    submission_status = "AC"
                    if status == "tick-icon":
                        submission_status = "AC"
                    elif status == "cross-icon":
                        submission_status = "WA"
                    elif status == "alert-icon":
                        submission_status = "CE"
                    elif status == "runtime-error":
                        submission_status = "RE"
                    elif status == "clock_error":
                        submission_status = "TLE"
                    else:
                        submission_status = "OTH"
                    append(submission_status)

                    # Question points
                    pts = i.contents[2].contents[0].contents
                    try:
                        if len(pts) >= 5:
                            points = pts[2] + " " + pts[4]
                        else:
                            points = pts[2]
                    except IndexError:
                        if submission_status == "AC":
                            points = "100"
                        else:
                            points = "0"
                    append(points)

                    # Language
                    append(i.contents[3].contents[0].strip())

                    # View code link
                    view_link = ""
                    append(view_link)

                    it += 1
            return submissions

# =============================================================================
