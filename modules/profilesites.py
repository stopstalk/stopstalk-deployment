import re, requests, ast, time
import parsedatetime as pdt
import datetime
from datetime import date
import bs4
import utilities

class Profile(object):
    def __init__(self, site="", handle=""):

        self.site = None
        self.handle = None

        if site in utilities.SITES:
            self.handle = handle
            self.site = site

    @staticmethod
    def parsetime(time_str):
        try:
            dt = datetime.datetime.strptime(time_str, "%I:%M %p %d/%m/%y")
            return dt
        except ValueError:
            cal = pdt.Calendar()
            dt, flags = cal.parseDT(time_str)
            assert flags
            return dt

    def codechef(self, last_retrieved):

        if self.handle:
            handle = self.handle
        else:
            return {}

        user_url = "http://www.codechef.com/recent/user?user_handle=" + handle
        while 1:
            try:
                tmp = requests.get(user_url, headers={"User-Agent": "Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5"}, proxies=utilities.PROXY)
                if tmp.status_code == 200:
                    break
            except:
                continue

        d = ast.literal_eval(tmp.text)
        max_page = d["max_page"]
        submissions = {handle: {}}
        it = 1

        for page in xrange(0, max_page):
            user_url = "http://www.codechef.com/recent/user?user_handle=" + handle + "&page=" + str(page)
            while 1:
                try:
                    tmp = requests.get(user_url, headers={"User-Agent": "Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5"}, proxies=utilities.PROXY)
                    if tmp.status_code == 200:
                        break
                except:
                    continue
            d = ast.literal_eval(tmp.text)

            d = d["content"]
            submissions[handle][page] = {}
            x = bs4.BeautifulSoup(d)
            for i in x.find_all("tr"):
                try:
                    if i['class'][0] == "kol":
                        submissions[handle][page][it] = []
                        submission = submissions[handle][page][it]
                        # tos = time_of_submission
                        tos = i.contents[0].contents[0]
                        tos = str(ast.literal_eval(repr(tos).replace("\\", "")))
                        tos = Profile.parsetime(tos)
                        curr = time.strptime(str(tos), "%Y-%m-%d %H:%M:%S")

                        if curr <= last_retrieved:
                            return submissions
                        submission.append(str(tos))

                        # Problem name/url
                        prob = i.contents[1].contents[0]
                        prob["href"] = "http://www.codechef.com" + prob["href"]
                        submission.append(eval(repr(prob["href"]).replace("\\", "")))
                        try:
                            submission.append(prob.contents[0])
                        except IndexError:
                            submission.append("")

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
                        submission.append(st)

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
                        submission.append(points)

                        # Language
                        submission.append(i.contents[3].contents[0].strip())
                        it += 1
                except KeyError:
                    pass
        return submissions

    def codeforces(self, last_retrieved):

        if self.handle:
            handle = self.handle
        else:
            return {}

        page = 1
        previd = -1

        it = 1
        submissions = {handle: {}}
        while 1:
            while 1:

                url = "http://codeforces.com/submissions/" + handle + "/page/" + str(page)
                try:
                    tmp = requests.get(url, proxies=utilities.PROXY)
                    soup = bs4.BeautifulSoup(tmp.text)
                    if tmp.status_code == 200:
                        break
                except:
                    continue

            tbody = None
            for i in soup.findAll("table", {"class": "status-frame-datatable"}):
                tbody = i
            if tbody is None:
                break
            flag = 0
            page += 1
            row = 0
            submissions[handle][page] = {}

            for i in tbody:
                if isinstance(i, bs4.element.Tag):

                    if i.contents[1].contents[0] == "#":
                        continue

                    submissions[handle][page][it] = []
                    submission = submissions[handle][page][it]

                    if row == 0:
                        try:
                            currid = i.contents[1].contents[1].contents[0]
                            if currid == previd:
                                flag = 1
                                break
                        except IndexError:
                            continue
                    previd = currid
                    row += 1

                    # Time of submission
                    tos = i.contents[3].contents[0].strip()
                    curr = time.strptime(str(tos), "%Y-%m-%d %H:%M:%S")
                    curr = time.gmtime(time.mktime(curr) + 480 * 60)

                    if curr <= last_retrieved:
                        return submissions
                    submission.append(str(time.strftime("%Y-%m-%d %H:%M:%S", curr)))

                    # Problem
                    prob = i.contents[7].contents[1]
                    prob["href"] = "http://codeforces.com" + prob["href"]
                    submission.append(eval(repr(prob["href"]).replace("\\", "")))
                    submission.append(prob.contents[0].strip())

                    # Submission Status
                    status = i.contents[11].contents[1].attrs["submissionverdict"]
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
                    else:
                        st = "OTH"
                    submission.append(st)

                    if st == "AC":
                        points = "100"
                    else:
                        if st == "HCK":
                            points = "-50"
                        else:
                            points = "0"
                    submission.append(points)
                    it += 1

                    # Language
                    lang = i.contents[9].contents[0].strip()
                    submission.append(lang)

            if flag == 1:
                break
        return submissions

    def spoj(self, last_retrieved):

        if self.handle:
            handle = self.handle
        else:
            return {}

        submissions = {handle: {}}
        start = 0
        it = 1

        previd = -1
        currid = 0
        page = 0
        url = "https://www.spoj.com/users/" + handle
        tmpreq = requests.get(url, proxies=utilities.PROXY)

        # Bad but correct way of checking if the handle exists
        if tmpreq.text.find("History of submissions") == -1:
            return submissions

        while 1:
            flag = 0
            url = "https://www.spoj.com/status/" + handle + "/all/start=" + str(start)
            start += 20
            t = requests.get(url, proxies=utilities.PROXY)
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
                    submission.append(str(tos))

                    # Problem URL
                    uri = i.contents[5].contents[0]
                    uri["href"] = "http://www.spoj.com" + uri["href"]
                    submission.append(eval(repr(uri["href"]).replace("\\", "")))
                    submission.append(uri.contents[0].strip())

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

                    submission.append(st)

                    # Question Points
                    if st == "AC":
                        points = "100"
                    else:
                        points = "0"
                    submission.append(points)

                    # Language
                    submission.append(i.contents[12].contents[1].contents[0])

                    it += 1
            page += 1
            if flag == 1:
                break
        return submissions

    def hackerearth(self, last_retrieved):

        if self.handle:
            handle = self.handle
        else:
            return {}

        url = "https://www.hackerearth.com/submissions/" + handle
        t = requests.get(url, proxies=utilities.PROXY)
        tmp_string = t.headers['set-cookie']
        csrf_token = re.findall("csrftoken=\w*", tmp_string)[0][10:]
        url = "https://www.hackerearth.com/AJAX/feed/newsfeed/submission/user/" + handle + "/"

        response = {}
        response["host"] = "www.hackerearth.com"
        response["user-agent"] = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:40.0) Gecko/20100101 Firefox/40.0"
        response["accept"] = "application/json, text/javascript, */*; q=0.01"
        response["accept-language"] = "en-US,en;q=0.5"
        response["accept-encoding"] = "gzip, deflate"
        response["content-type"] = "application/x-www-form-urlencoded"
        response["X-CSRFToken"] = csrf_token
        response["X-Requested-With"] = "XMLHttpRequest"
        response["Referer"] = "https://www.hackerearth.com/submissions/raj454raj/"
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
                                proxies=utilities.PROXY,
                                headers=response)

            try:
                final_json = tmp.json()
            except:
                break

            if final_json["count"] == 0:
                break

            for feed_number in xrange(20):

                submissions[handle][i / 20][it] = []
                submission = submissions[handle][i / 20][it]

                try:
                    final = bs4.BeautifulSoup((tmp.json()["feed" + str(feed_number)]))
                except KeyError:
                    break

                all_as = final.find_all("a")
                all_tds = final.find_all("td")
                tos = all_tds[-1].contents[1]["title"]
                time_stamp = time.strptime(str(tos), "%Y-%m-%d %H:%M:%S")

                if time_stamp <= last_retrieved:
                    return submissions
                submission.append(str(tos))

                problem_link = "https://hackerearth.com" + all_as[1]["href"]
                submission.append(problem_link)
                problem_name = all_as[1].contents[0]
                submission.append(problem_name)

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
                submission.append(status)

                if status == "AC":
                    points = "100"
                else:
                    points = "0"
                submission.append(points)

                language = all_tds[5].contents[0]
                submission.append(language)
                it += 1
        return submissions

    def hackerrank(self, last_retrieved):

        if self.handle:
            handle = self.handle
        else:
            return {}

        tmp = requests.get("https://www.hackerrank.com/rest/hackers/" + handle + "/recent_challenges?offset=0&limit=50000000")

        all_submissions = tmp.json()["models"]

        submissions = {handle: {1 : {}}}
        it = 0
        for row in all_submissions:

            submission = submissions[handle][1]
            submission[it] = []
            submission = submission[it]

            time_stamp = row["created_at"][:-5].split("T")
            curr = time.strptime(time_stamp[0] + " " + time_stamp[1],
                                 "%Y-%m-%d %H:%M:%S")

            if curr <= last_retrieved:
                return submissions
            submission.append(" ".join(time_stamp))

            submission.append("https://hackerrank.com/challenges/" + row["slug"])
            submission.append(row["name"])
            submission.append("AC")
            submission.append("100")
            submission.append("-")
            it += 1

        return submissions
