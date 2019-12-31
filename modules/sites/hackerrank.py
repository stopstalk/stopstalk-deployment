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
    site_name = "HackerRank"

    # -------------------------------------------------------------------------
    def __init__(self, handle=""):
        """
            @param handle (String): HackerRank handle
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

        if problem_link.__contains__("/contests/"):
            # If the problem_link is a contest URL
            url = problem_link.replace("https://www.hackerrank.com", "")
            url = "https://www.hackerrank.com/rest/" + url
        else:
            # Practice problem URL
            slug = problem_link.split("/")[-1]
            url = "https://www.hackerrank.com/rest/contests/master/challenges/" + slug

        response = get_request(url)
        if response in REQUEST_FAILURES:
            return ["-"]

        response = response.json()

        model = response["model"]
        track = model["track"]
        primary_contest = model["primary_contest"]
        all_tags = ["-"]

        if track:
            # If the problem is a practice problem
            all_tags = [track["name"]]
        elif primary_contest:
            if primary_contest["track"]:
                # If the problem is a contest problem with track
                all_tags = [primary_contest["track"]["name"]]
            elif primary_contest["name"]:
                # If the problem is a contest problem without track
                # Then consider contest name as tag
                all_tags = [primary_contest["name"]]

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
        if problem_link.__contains__("contests"):
            rest_url = problem_link.replace("contests/",
                                            "rest/contests/")
        else:
            rest_url = problem_link.replace("challenges/",
                                            "rest/contests/master/challenges/")
        response = get_request(rest_url)
        if response in REQUEST_FAILURES:
            return editorial_link

        editorial_present = response.json()["model"]["is_editorial_available"]
        return problem_link + "/editorial/" if editorial_present else None

    # -------------------------------------------------------------------------
    @staticmethod
    def is_invalid_handle(handle):
        url = "https://www.hackerrank.com/rest/hackers/" + \
              handle + \
              "/recent_challenges?offset=0&limit=2"
        response = get_request(url)
        if response in REQUEST_FAILURES:
            return True
        return False

    # -------------------------------------------------------------------------
    @staticmethod
    def rating_graph_data(handle):
        website = "https://www.hackerrank.com/"
        url = "%srest/hackers/%s/rating_histories_elo" % (website, handle)
        response = get_request(url)
        if response in REQUEST_FAILURES:
            return response

        response = response.json()["models"]

        hackerrank_graphs = []
        for contest_class in response:
            final_json = {}
            for contest in contest_class["events"]:
                time_stamp = contest["date"][:-5].split("T")
                time_stamp = datetime.datetime.strptime(time_stamp[0] + " " + time_stamp[1],
                                                        "%Y-%m-%d %H:%M:%S")
                # Convert UTC to IST
                time_stamp += datetime.timedelta(hours=5, minutes=30)
                time_stamp = str(time_stamp)
                final_json[time_stamp] = {"name": contest["contest_name"],
                                          "url": website + contest["contest_slug"],
                                          "rating": str(contest["rating"]),
                                          "rank": contest["rank"]}

            graph_name = "HackerRank - %s" % contest_class["category"]
            hackerrank_graphs.append({"title": graph_name,
                                      "data": final_json})

        return hackerrank_graphs


    # -------------------------------------------------------------------------
    def get_submissions(self, last_retrieved, is_daily_retrieval):
        """
            Retrieve HackerRank submissions after last retrieved timestamp

            @param last_retrieved (DateTime): Last retrieved timestamp for the user
            @param is_daily_retrieval (Boolean): If this call is from daily retrieval cron

            @return (Dict): Dictionary of submissions containing all the
                            information about the submissions
        """

        handle = self.handle
        url = "https://www.hackerrank.com/rest/hackers/" + \
              handle + \
              "/recent_challenges"
        request_params = {"limit": "5", "response_version": "v2"}

        submissions = []
        next_cursor = "null"

        for i in xrange(1000):

            request_params["cursor"] = next_cursor
            response = get_request(url,
                                   params=request_params,
                                   is_daily_retrieval=is_daily_retrieval)

            if response in REQUEST_FAILURES:
                return response
            next_cursor = response.json()["cursor"]
            for row in response.json()["models"]:
                # Time of submission
                # @Todo: This is ugly
                time_stamp = row["created_at"][:-10].split("T")
                time_stamp = time.strptime(time_stamp[0] + " " + time_stamp[1],
                                           "%Y-%m-%d %H:%M:%S")
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

                submissions.append((str(time_stamp),
                                    "https://www.hackerrank.com" + row["url"],
                                    row["name"],
                                    "AC",
                                    "100",
                                    "-",
                                    ""))

            if response.json()["last_page"] == True:
                break

        return submissions

# =============================================================================
