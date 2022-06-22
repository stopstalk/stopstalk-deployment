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
    site_name = "HackerEarth"

    # -------------------------------------------------------------------------
    def __init__(self, handle=""):
        """
            @param handle (String): HackerEarth Handle
        """

        self.site = Profile.site_name
        self.handle = handle

    # -------------------------------------------------------------------------
    @staticmethod
    def is_valid_url(url):
        return url.__contains__("hackerearth.com/")

    # -------------------------------------------------------------------------
    @staticmethod
    def is_website_down():
        """
            @return (Boolean): If the website is down
        """
        return (Profile.site_name in current.REDIS_CLIENT.smembers("disabled_retrieval"))


    # -------------------------------------------------------------------------
    @staticmethod
    def get_headers(response, referer):
        cookie_value = response.headers["set-cookie"]
        csrf_token = re.findall(r"csrftoken=\w*", cookie_value)[0][10:]
        return {
            "host": "www.hackerearth.com",
            "user-agent": COMMON_USER_AGENT,
            "accept": "application/json, text/javascript, */*; q=0.01",
            "accept-language": "en-US,en;q=0.5",
            "accept-encoding": "gzip, deflate",
            "content-type": "application/x-www-form-urlencoded",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": referer,
            "Cookie": cookie_value,
            "Connection": "keep-alive",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
            "X-CSRFToken": csrf_token
        }

    # -------------------------------------------------------------------------
    @staticmethod
    def get_tags(meta_data):
        if "tags" not in meta_data:
            return []

        tags = meta_data["tags"].split(",")

        if len(tags) == 1 and tags[0].strip() == '':
            return []
        else:
            return [x.strip() for x in tags]

    # -------------------------------------------------------------------------
    @staticmethod
    def get_editorial_link(meta_data, problem_link):
        if "editorial" not in meta_data or meta_data["editorial"] == "" or \
           meta_data["editorial"]["state"] == "do-not-exist":
            return None
        else:
            return problem_link + "editorial/"

    # -------------------------------------------------------------------------
    @staticmethod
    def get_problem_setters(response):
        author_url = response["author"]
        problem_setters = None if author_url is None else [author_url["profile_url"][2:]]
        return problem_setters

    # -------------------------------------------------------------------------
    @staticmethod
    def get_problem_details(**args):
        """
            Get problem_details given a problem link

            @param args (Dict): Dict containing problem link
            @return (Dict): Details of the problem returned in a dictionary
        """
        tags = []
        editorial_link = None
        problem_setters = None
        problem_link = args["problem_link"]

        if "tags" in args["update_things"] or \
           "editorial_link" in args["update_things"]:
            response = get_request(problem_link)
            if response in REQUEST_FAILURES:
                return dict(tags=tags,
                            editorial_link=None,
                            problem_setters=None)

            import re, json
            try:
                meta_data_json = re.search("problemData: .*}",
                                           response.text).group().replace("problemData: ", "")
                meta_data = json.loads(meta_data_json)
            except Exception as e:
                print "Exception in re parsing", e
                return dict(tags=tags,
                            editorial_link=None,
                            problem_setters=None)

            tags = Profile.get_tags(meta_data)
            editorial_link = Profile.get_editorial_link(meta_data, problem_link)

        if "problem_setters" in args["update_things"]:
            api_link = "https://www.hackerearth.com/practice/api/problems/" + \
                       "/".join(problem_link.split("/")[-3:-1]) + "/"

            response = get_request(api_link)
            if response in REQUEST_FAILURES:
                return dict(tags=tags,
                            editorial_link=None,
                            problem_setters=None)

            response = response.json()
            problem_setters = Profile.get_problem_setters(response)

        return dict(tags=tags,
                    editorial_link=editorial_link,
                    problem_setters=problem_setters)

    # -------------------------------------------------------------------------
    @staticmethod
    def is_invalid_handle(handle):
        url = "https://www.hackerearth.com/submissions/" + handle
        response = get_request(url)
        if response in REQUEST_FAILURES:
            return True
        return False

    # -------------------------------------------------------------------------
    @staticmethod
    def rating_graph_data(handle):
        url = "https://www.hackerearth.com/ratings/AJAX/rating-graph/" + handle
        response = get_request(url)
        if response in REQUEST_FAILURES:
            return response

        if response.text == "":
            return NOT_FOUND

        contest_data = eval(re.findall(r"var dataset = \[.*?\]", response.text)[0][14:])
        if len(contest_data) == 0:
            return []

        hackerearth_data = {}
        for contest in contest_data:
            time_stamp = str(datetime.datetime.strptime(contest["event_start"], "%d %b %Y, %I:%M %p") + datetime.timedelta(minutes=330))
            url = "https://www.hackerearth.com" + contest["event_url"]
            hackerearth_data[time_stamp] = {"name": contest["event_title"],
                                            "rating": contest["rating"],
                                            "url": url,
                                            "rank": contest["rank"]}

        return [{"title": "HackerEarth",
                 "data": hackerearth_data}]

    # -------------------------------------------------------------------------
    def get_submissions(self, last_retrieved, is_daily_retrieval):
        """
            Retrieve HackerEarth submissions after last retrieved timestamp
            @param last_retrieved (DateTime): Last retrieved timestamp for the user
            @param is_daily_retrieval (Boolean): If this call is from daily retrieval cron

            @return (Dict): Dictionary of submissions containing all the
                            information about the submissions
        """

        handle = self.handle

        url = "https://www.hackerearth.com/submissions/%s/" % handle
        response = get_request(url, is_daily_retrieval=is_daily_retrieval)

        if response in REQUEST_FAILURES:
            return response

        headers = Profile.get_headers(response, url)

        submissions = []
        for page_number in xrange(1, 1000):
            url = "https://www.hackerearth.com/AJAX/feed/newsfeed/submission/user/" + handle + "/?page=" + str(page_number)

            tmp = get_request(url,
                              headers=headers,
                              timeout=20,
                              is_daily_retrieval=is_daily_retrieval)

            if tmp in REQUEST_FAILURES:
                return tmp

            json_response = tmp.json()
            if json_response["status"] == "ERROR":
                break

            body = json_response["data"]
            soup = bs4.BeautifulSoup(body, "lxml")

            trs = soup.find("tbody").find_all("tr")
            for tr in trs:

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
                                               datetime.timedelta(minutes=330)
                curr = time.strptime(str(time_stamp), "%Y-%m-%d %H:%M:%S")

                if curr <= last_retrieved:
                    return submissions

                # Problem Name/URL
                problem_link = "https://www.hackerearth.com" + all_as[1]["href"]
                problem_name = all_as[1].contents[0]

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

                if status == "AC":
                    points = "100"
                else:
                    points = "0"

                language = all_tds[5].contents[0]

                submissions.append((str(time_stamp),
                                    problem_link,
                                    problem_name,
                                    status,
                                    points,
                                    language,
                                    "https://www.hackerearth.com/submission/" + \
                                    tr["id"].split("-")[-1]))

        return submissions

# =============================================================================
