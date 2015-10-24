import re, requests, ast, time
import parsedatetime as pdt
import datetime
import bs4
import gevent
from gevent import monkey
from gluon import current

gevent.monkey.patch_all(thread=False)
user_agent = "Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5"

"""
    @ToDo: Current framework is very bad
"""

class Profile(object):
    """
        Class containing methods for retrieving
        submissions of user
    """

    # -------------------------------------------------------------------------
    def __init__(self, site="", handle=""):

        self.site = None
        self.handle = None
        self.submissions = {handle: {}}
        self.retrieve_failed = False

        if site in current.SITES:
            self.handle = handle
            self.site = site

    # -------------------------------------------------------------------------
    @staticmethod
    def parsetime(time_str):
        """
            Try to parse any generalised time to
            standard format.
            For now used by Codechef
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
    def get_request(url, headers={}):
        """
            Make a HTTP GET request to a url
        """

        MAX_TRIES_ALLOWED = current.MAX_TRIES_ALLOWED
        i = 0

        while i < MAX_TRIES_ALLOWED:
            try:
                response = requests.get(url,
                                        headers=headers,
                                        proxies=current.PROXY)
            except RuntimeError:
                return -1

            if response.status_code == 200:
                return response
            i += 1

        if response.status_code == 404:
            return {}

        return -1

    # -------------------------------------------------------------------------
    def parallelize_codechef(self, handle, page):
        """
            Helper function for retrieving codechef submissions parallely
        """

        if self.retrieve_failed:
            return

        url = "https://www.codechef.com/recent/user?user_handle=" + \
               handle + \
               "&page=" + \
               str(page)

        tmp = Profile.get_request(url, headers={"User-Agent": user_agent})

        # GET request failed
        if tmp == -1:
            self.retrieve_failed = True
            return

        d = ast.literal_eval(tmp.text)["content"]

        it = 1
        self.submissions[handle][page] = {}
        x = bs4.BeautifulSoup(d)

        for i in x.find_all("tr"):
            try:
                if i["class"][0] == "kol":

                    self.submissions[handle][page][it] = []
                    submission = self.submissions[handle][page][it]
                    append = submission.append

                    # tos = time_of_submission
                    tos = i.contents[0].contents[0]
                    tos = str(ast.literal_eval(repr(tos).replace("\\", "")))
                    tos = Profile.parsetime(tos)
                    append(str(tos))

                    # Problem name/url
                    prob = i.contents[1].contents[0]
                    prob["href"] = "http://www.codechef.com" + prob["href"]
                    append(eval(repr(prob["href"]).replace("\\", "")))
                    try:
                        append(prob.contents[0])
                    except IndexError:
                        append("")

                    # Submission status
                    stat = i.contents[2].contents[0]
                    stat = stat.find("img")["src"]
                    stat = repr(stat).replace("\\", "")
                    stat = stat[7:-5]
                    st = "AC"
                    if stat == "tick-icon":
                        st = "AC"
                    elif stat == "cross-icon":
                        st = "WA"
                    elif stat == "alert-icon":
                        st = "CE"
                    elif stat == "runtime-error":
                        st = "RE"
                    elif stat == "clock_error":
                        st = "TLE"
                    else:
                        st = "OTH"
                    append(st)

                    # Question points
                    pts = i.contents[2].contents[0].contents
                    try:
                        if  len(pts) >= 5:
                            points = pts[2] + " " + pts[4]
                        else:
                            points = pts[2]
                    except IndexError:
                        if st == "AC":
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
            except KeyError:
                pass

    # -------------------------------------------------------------------------
    def codechef(self, last_retrieved):

        if self.retrieve_failed:
            return -1

        if self.handle:
            handle = self.handle
        else:
            return -1

        user_url = "http://www.codechef.com/recent/user?user_handle=" + handle

        tmp = Profile.get_request(user_url, headers={"User-Agent": user_agent})

        if tmp == -1:
            return -1

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
                                            i))
            gevent.joinall(threads)
            return self.submissions

        else:
            for page in xrange(0, max_page):
                user_url = "http://www.codechef.com/recent/user?user_handle=" + \
                           handle + \
                           "&page=" + \
                           str(page)

                tmp = Profile.get_request(user_url, headers={"User-Agent": user_agent})

                if tmp == -1:
                    return -1

                d = ast.literal_eval(tmp.text)["content"]

                submissions[handle][page] = {}
                x = bs4.BeautifulSoup(d)
                for i in x.find_all("tr"):
                    try:
                        if i["class"][0] == "kol":

                            submissions[handle][page][it] = []
                            submission = submissions[handle][page][it]
                            append = submission.append

                            # tos = time_of_submission
                            tos = i.contents[0].contents[0]
                            tos = str(ast.literal_eval(repr(tos).replace("\\", "")))

                            # Do not retrieve any further because this leads to ambiguity
                            # If 2 hours ago => 2 hours 20 mins or 2 hours 14 mins ...
                            # Let the user come back later when the datetime is exact
                            # This prevents from redundant addition into database
                            # @ToDo: For now we are allowing redundant submissions
                            #        for codechef :/ . Find a way to change it.
                            #if tos.__contains__("hours"):
                            #   continue

                            tos = Profile.parsetime(tos)
                            curr = time.strptime(str(tos), "%Y-%m-%d %H:%M:%S")

                            if curr <= last_retrieved:
                                return submissions
                            append(str(tos))

                            # Problem name/url
                            prob = i.contents[1].contents[0]
                            prob["href"] = "http://www.codechef.com" + prob["href"]
                            append(eval(repr(prob["href"]).replace("\\", "")))
                            try:
                                append(prob.contents[0])
                            except IndexError:
                                append("")

                            # Submission status
                            stat = i.contents[2].contents[0]
                            stat = stat.find("img")["src"]
                            stat = repr(stat).replace("\\", "")
                            stat = stat[7:-5]
                            st = "AC"
                            if stat == "tick-icon":
                                st = "AC"
                            elif stat == "cross-icon":
                                st = "WA"
                            elif stat == "alert-icon":
                                st = "CE"
                            elif stat == "runtime-error":
                                st = "RE"
                            elif stat == "clock_error":
                                st = "TLE"
                            else:
                                st = "OTH"
                            append(st)

                            # Question points
                            pts = i.contents[2].contents[0].contents
                            try:
                                if  len(pts) >= 5:
                                    points = pts[2] + " " + pts[4]
                                else:
                                    points = pts[2]
                            except IndexError:
                                if st == "AC":
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
                    except KeyError:
                        pass
            return submissions

    # -------------------------------------------------------------------------
    def codeforces(self, last_retrieved):

        if self.handle:
            handle = self.handle
        else:
            return -1

        url = "http://codeforces.com/api/user.status?handle=" + \
              handle + \
              "&from=1&count=5000"

        tmp = Profile.get_request(url, headers={"User-Agent": user_agent})

        if tmp == -1:
            return -1

        submissions = {handle: {1: {}}}
        all_submissions = tmp.json()
        if all_submissions["status"] != "OK":
            return submissions
        all_submissions = all_submissions["result"]
        it = 0
        for row in all_submissions:

            submissions[handle][1][it] = []
            submission = submissions[handle][1][it]
            append = submission.append

            curr = time.gmtime(row["creationTimeSeconds"] + 330 * 60)
            if curr <= last_retrieved:
                return submissions
            # Time of submission
            append(str(time.strftime("%Y-%m-%d %H:%M:%S", curr)))
            time_stamp = time.strftime("%Y-%m-%d %H:%M:%S", curr)

            arg = "problem/"
            if len(str(row["contestId"])) > 3:
                arg = "gymProblem/"

            # Problem Name/URL
            problem_link = "http://codeforces.com/problemset/" + arg + \
                           str(row["contestId"]) + "/" + \
                           row["problem"]["index"]

            append(problem_link)
            problem_name = row["problem"]["name"]
            append(problem_name)

            # Problem status
            status = row["verdict"]
            st = "AC"
            if status == "OK":
                st = "AC"
            elif status == "WRONG_ANSWER":
                st = "WA"
            elif status == "COMPILATION_ERROR":
                st = "CE"
            elif status == "SKIPPED":
                st = "SK"
            elif status == "RUNTIME_ERROR":
                st = "RE"
            elif status == "TIME_LIMIT_EXCEEDED":
                st = "TLE"
            elif status == "CHALLENGED":
                st = "HCK"
            elif status == "MEMORY_LIMIT_EXCEEDED":
                st = "MLE"
            elif status == "TESTING":
                continue
            else:
                st = "OTH"
            append(st)

            # Points
            if st == "AC":
                points = "100"
            elif st == "HCK":
                points = "-50"
            else:
                points = "0"
            append(points)

            # Language
            append(row["programmingLanguage"])

            # View code link
            view_link = "http://codeforces.com/contest/" + \
                        str(row["contestId"]) + \
                        "/submission/" + \
                        str(row["id"])
            append(view_link)

            it += 1

        return submissions

    # -------------------------------------------------------------------------
    def spoj(self, last_retrieved):

        if self.handle:
            handle = self.handle
        else:
            return -1

        submissions = {handle: {}}
        start = 0
        it = 1

        previd = -1
        currid = 0
        page = 0
        url = "https://www.spoj.com/users/" + handle
        tmpreq = Profile.get_request(url)

        if tmpreq == -1:
            return -1

        # Bad but correct way of checking if the handle exists
        if tmpreq.text.find("History of submissions") == -1:
            return submissions

        while 1:
            flag = 0
            url = "https://www.spoj.com/status/" + \
                  handle + \
                  "/all/start=" + \
                  str(start)

            start += 20
            t = Profile.get_request(url)
            if t == -1:
                return -1

            soup = bs4.BeautifulSoup(t.text)
            table_body = soup.find("tbody")

            # Check if the page retrieved has no submissions
            if len(table_body) == 1:
                return submissions

            row = 0
            submissions[handle][page] = {}
            for i in table_body:
                submissions[handle][page][it] = []
                submission = submissions[handle][page][it]
                append = submission.append

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
                    if curr <= last_retrieved:
                        return submissions
                    append(str(tos))

                    # Problem Name/URL
                    uri = i.contents[5].contents[0]
                    uri["href"] = "http://www.spoj.com" + uri["href"]
                    append(eval(repr(uri["href"]).replace("\\", "")))
                    append(uri.contents[0].strip())

                    # Problem Status
                    status = str(i.contents[6])
                    if status.__contains__("accepted"):
                        st = "AC"
                    elif status.__contains__("wrong"):
                        st = "WA"
                    elif status.__contains__("compilation"):
                        st = "CE"
                    elif status.__contains__("runtime"):
                        st = "RE"
                    elif status.__contains__("time limit"):
                        st = "TLE"
                    else:
                        st = "OTH"

                    append(st)

                    # Question Points
                    if st == "AC":
                        points = "100"
                    else:
                        points = "0"
                    append(points)

                    # Language
                    append(i.contents[12].contents[1].contents[0])

                    # View code Link
                    view_link = ""
                    append(view_link)

                    it += 1

            page += 1

            if flag == 1:
                break

        return submissions

    # -------------------------------------------------------------------------
    def hackerearth(self, last_retrieved):

        if self.handle:
            handle = self.handle
        else:
            return {}

        url = "https://www.hackerearth.com/submissions/" + handle
        t = Profile.get_request(url)
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
                problem_link = "https://hackerearth.com" + all_as[1]["href"]
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
                view_link = "https://hackerearth.com" + \
                            all_as[-1]["href"]
                append(view_link)

                it += 1

        return submissions

    # -------------------------------------------------------------------------
    def hackerrank(self, last_retrieved):

        if self.handle:
            handle = self.handle
        else:
            return -1

        url = "https://www.hackerrank.com/rest/hackers/" + \
              handle + \
              "/recent_challenges?offset=0&limit=50000"

        tmp = Profile.get_request(url)
        if tmp == -1:
            return -1

        all_submissions = tmp.json()["models"]

        submissions = {handle: {1 : {}}}
        it = 0
        for row in all_submissions:

            submission = submissions[handle][1]
            submission[it] = []
            submission = submission[it]
            append = submission.append

            # Time of submission
            time_stamp = row["created_at"][:-5].split("T")
            curr = time.strptime(time_stamp[0] + " " + time_stamp[1],
                                 "%Y-%m-%d %H:%M:%S")
            if curr <= last_retrieved:
                return submissions
            append(" ".join(time_stamp))

            # Problem link
            append("https://hackerrank.com/challenges/" + row["slug"])

            # Problem name
            append(row["name"])

            # Status
            # HackerRank only gives the list of solved problems
            append("AC")

            # Points
            append("100")

            # Language
            append("-")

            # View code link
            append("")

            it += 1

        return submissions
