"""
    Copyright (c) 2015 Raj Patel(raj454raj@gmail.com), StopStalk

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

        self.site = "HackerEarth"
        self.handle = handle

    # -------------------------------------------------------------------------
    @staticmethod
    def get_tags(problem_link):

        response = get_request(problem_link)
        if response == -1 or response == {}:
            return ["-"]

        b = BeautifulSoup(response.text)
        try:
            tags = b.find_all("div", class_="problem-tags")[0]
        except IndexError:
            return ["-"]
        lis = tags.find_all("li")
        all_tags = []
        for li in lis:
            if li.contents[0] != "No tags":
                all_tags.append(li.contents[0])

        if all_tags == []:
            all_tags = ["-"]

        return all_tags

    # -------------------------------------------------------------------------
    def get_submissions(self, last_retrieved):

        if self.handle:
            handle = self.handle
        else:
            return {}

        url = "https://www.hackerearth.com/submissions/" + handle
        t = get_request(url)
        if t == -1 or t == {}:
            return t

        tmp_string = t.headers["set-cookie"]
        csrf_token = re.findall("csrftoken=\w*", tmp_string)[0][10:]
        url = "https://www.hackerearth.com/AJAX/feed/newsfeed/submission/user/" + handle + "/"

        response = {}
        response["host"] = "www.hackerearth.com"
        response["user-agent"] = user_agent
        response["accept"] = "application/json, text/javascript, */*; q=0.01"
        response["accept-language"] = "en-US,en;q=0.5"
        response["accept-encoding"] = "gzip, deflate"
        response["content-type"] = "application/x-www-form-urlencoded"
        response["X-CSRFToken"] = csrf_token
        response["X-Requested-With"] = "XMLHttpRequest"
        response["Referer"] = "https://www.hackerearth.com/submissions/" + handle + "/"
        response["Connection"] = "keep-alive"
        response["Pragma"] = "no-cache"
        response["Cache-Control"] = "no-cache"
        response["Cookie"] = tmp_string

        it = 1
        submissions = {handle: {}}
        for i in xrange(0, 10000, 20):
            submissions[handle][i / 20] = {}
            data = {"index": str(i)}

            tmp = requests.post(url,
                                data=data,
                                proxies=current.PROXY,
                                headers=response)

            if tmp.status_code != 200:
                return -1
            try:
                final_json = tmp.json()
            except:
                break

            if final_json["count"] == 0:
                break

            for feed_number in xrange(20):

                submissions[handle][i / 20][it] = []
                submission = submissions[handle][i / 20][it]
                append = submission.append

                try:
                    feed_key = "feed" + str(feed_number)
                    final = bs4.BeautifulSoup((tmp.json()[feed_key]))
                except KeyError:
                    break

                all_as = final.find_all("a")
                all_tds = final.find_all("td")
                tos = all_tds[-1].contents[1]["title"]
                time_stamp = time.strptime(str(tos), "%Y-%m-%d %H:%M:%S")

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

                # View code link
                view_link = "https://www.hackerearth.com" + \
                            all_as[-1]["href"]
                append(view_link)

                it += 1

        return submissions
