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
            @param handle (String): HackerEarth Handle
        """

        self.site = "HackerEarth"
        self.handle = handle

    # -------------------------------------------------------------------------
    @staticmethod
    def get_tags(problem_link):
        """
            Get tags given a problem link

            @param problem_link (String): Problem URL
            @return (List): List of tags for the Problem
        """

        response = get_request(problem_link)
        if response in REQUEST_FAILURES:
            return ["-"]

        b = BeautifulSoup(response.text, "lxml")
        try:
            tags = b.find_all("div", class_="problem-tags")[0]
        except IndexError:
            return ["-"]
        lis = tags.find_all("span")[1:]
        all_tags = []
        for li in lis:
            if li.contents[0] != "No tags":
                all_tags.append(li.contents[0].strip(", "))

        if all_tags == []:
            all_tags = ["-"]

        return all_tags

    # -------------------------------------------------------------------------
    @staticmethod
    def get_editorial_link(problem_link):
        """
            Get editorial link given a problem link

            @param problem_link (String): Problem URL
            @return (String/None): Editorial URL
        """
        return problem_link + "editorial/"

    # -------------------------------------------------------------------------
    def get_submissions(self, last_retrieved):
        """
            Retrieve HackerEarth submissions after last retrieved timestamp
            @param last_retrieved (DateTime): Last retrieved timestamp for the user
            @return (Dict): Dictionary of submissions containing all the
                            information about the submissions
        """

        handle = self.handle

        url = "https://www.hackerearth.com/submissions/" + handle
        t = get_request(url)

        if t in REQUEST_FAILURES:
            return t

        tmp_string = t.headers["set-cookie"]
        csrf_token = re.findall(r"csrftoken=\w*", tmp_string)[0][10:]

        headers = {"host": "www.hackerearth.com",
                   "user-agent": user_agent,
                   "accept": "application/json, text/javascript, */*; q=0.01",
                   "accept-language": "en-US,en;q=0.5",
                   "accept-encoding": "gzip, deflate",
                   "content-type": "application/x-www-form-urlencoded",
                   "X-CSRFToken": csrf_token,
                   "X-Requested-With": "XMLHttpRequest",
                   "Referer": "https://www.hackerearth.com/submissions/" + handle + "/",
                   "Connection": "keep-alive",
                   "Pragma": "no-cache",
                   "Cache-Control": "no-cache",
                   "Cookie": tmp_string}

        it = 1
        submissions = {handle: {}}
        for page_number in xrange(1, 1000):
            submissions[handle][page_number] = {}
            url = "https://www.hackerearth.com/AJAX/feed/newsfeed/submission/user/" + handle + "/?page=" + str(page_number)

            tmp = get_request(url, headers=headers)

            if tmp in REQUEST_FAILURES:
                return tmp

            json_response = tmp.json()
            if json_response["status"] == "ERROR":
                break

            body = json_response["data"]
            soup = bs4.BeautifulSoup(body, "lxml")

            trs = soup.find("tbody").find_all("tr")
            for tr in trs:

                submissions[handle][page_number][it] = []
                submission = submissions[handle][page_number][it]
                append = submission.append

                all_tds = tr.find_all("td")
                all_as = tr.find_all("a")
                time_stamp = all_tds[-1].contents[1]["title"]
                time_stamp = time.strptime(str(time_stamp), "%Y-%m-%d %H:%M:%S")

                # Time of submission
                time_stamp = datetime.datetime(time_stamp.tm_year,
                                               time_stamp.tm_mon,
                                               time_stamp.tm_mday,
                                               time_stamp.tm_hour,
                                               time_stamp.tm_min,
                                               time_stamp.tm_sec) + \
                                               datetime.timedelta(minutes=630)
                curr = time.strptime(str(time_stamp), "%Y-%m-%d %H:%M:%S")

                if curr <= last_retrieved:
                    return submissions
                append(str(time_stamp))

                # Problem Name/URL
                problem_link = "https://www.hackerearth.com" + all_as[1]["href"]
                append(problem_link)
                problem_name = all_as[1].contents[0]
                append(problem_name)

                # Status
                try:
                    status = all_tds[2].contents[1]["title"]
                except IndexError:
                    status = "Others"

                if status.__contains__("Accepted"):
                    status = "AC"
                elif status.__contains__("Partially"):
                    status = "PS"
                elif status.__contains__("Wrong"):
                    status = "WA"
                elif status.__contains__("Compilation"):
                    status = "CE"
                elif status.__contains__("Runtime"):
                    status = "RE"
                elif status.__contains__("Memory"):
                    status = "MLE"
                elif status.__contains__("Time"):
                    status = "TLE"
                else:
                    status = "OTH"
                append(status)

                # Points
                if status == "AC":
                    points = "100"
                else:
                    points = "0"
                append(points)

                # Language
                language = all_tds[5].contents[0]
                append(language)

                # View Link
                append("https://www.hackerearth.com/submission/" + \
                       tr["id"].split("-")[-1])

                it += 1

        return submissions

# =============================================================================
