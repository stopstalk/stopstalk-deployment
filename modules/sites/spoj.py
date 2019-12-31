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
    site_name = "Spoj"

    # -------------------------------------------------------------------------
    def __init__(self, handle=""):
        """
            @param handle (String): Spoj handle
        """

        self.site = Profile.site_name
        self.handle = handle
        self.submissions = []
        self.retrieval_failure = None

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
    @staticmethod
    def is_invalid_handle(handle):
        response = get_request("http://www.spoj.com/users/" + handle,
                               timeout=10)
        if response in REQUEST_FAILURES:
            return True
        # Bad but correct way of checking if the handle exists
        if response.text.find("History of submissions") == -1:
            return True
        return False

    # -------------------------------------------------------------------------
    def old_submission_retrieval(self, last_retrieved):
        """
            This will be used in case of dev environments and just in case we
            are facing issues with AWS Lambda
            @param last_retrieved (DateTime): Last retrieved timestamp for the user
            @return (List): List of submissions containing all the
                            information
        """
        start = 0
        self.submissions = []
        previd = -1
        currid = 0

        for i in xrange(1000):
            flag = 0
            url = current.SITES[self.site] + "status/" + \
                  self.handle + \
                  "/all/start=" + \
                  str(start)

            start += 20
            t = get_request(url,
                            timeout=10,
                            is_daily_retrieval=self.is_daily_retrieval)
            if t in REQUEST_FAILURES:
                return t

            soup = bs4.BeautifulSoup(t.text, "lxml")
            table_body = soup.find("tbody")

            # Check if the page retrieved has no submissions
            if len(table_body) == 1:
                return self.submissions

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
                        return self.submissions

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

                    self.submissions.append((tos,
                                             problem_link,
                                             uri.contents[0].strip(),
                                             submission_status,
                                             points,
                                             i.contents[12].contents[1].contents[0],
                                             ""))

            if flag == 1:
                break

        return self.submissions

    # -------------------------------------------------------------------------
    def new_submission_retrieval(self, last_retrieved, response_text):
        """
            This will be used in case of prod environment to get all the submissions
            of the user made on spoj after last_retrieved

            @param last_retrieved (DateTime): Last retrieved timestamp for the user
            @return (List): List of submissions containing all the
                            information
        """
        from gevent.coros import BoundedSemaphore
        import gevent

        # Send requests to AWS API gateway in batches of size AWS_LAMBDA_CONCURRENCY
        AWS_LAMBDA_CONCURRENCY = 200
        lambda_params = {"last_retrieved": last_retrieved,
                         "spoj_handle": self.handle}

        def _get_problem_names(response_text):
            soup = bs4.BeautifulSoup(response_text, "lxml")
            tds = soup.find_all("td")
            all_problem_names = []
            for td in tds:
                try:
                    atag = td.contents[0]
                    if re.match("/status/.*,%s/" % self.handle, atag["href"]) and \
                       atag.text != "":
                        all_problem_names.append(atag.text)
                except:
                    pass
            return all_problem_names

        def _get_problem_wise_submissions(semaphore, problem_slug):
            if self.retrieval_failure is not None:
                # If any one thread failed then fail the retrieval
                return

            def _lambda_result_map(submission):
                return [submission[0], # Time of submission
                        "https://www.spoj.com/problems/%s/" % problem_slug, # Problem link
                        submission[1], # Problem name
                        submission[2], # Submission status
                        submission[3], # Points
                        submission[4], # Language
                        ""]            # View link

            lambda_params["problem_slug"] = problem_slug
            try:
                response = get_request(current.spoj_lambda_url,
                                       params=lambda_params,
                                       timeout=30,
                                       is_daily_retrieval=self.is_daily_retrieval)
                if response in REQUEST_FAILURES:
                    self.retrieval_failure = response
                    return

                result = response.json()
                semaphore.acquire(timeout=5)
                self.submissions.extend(map(_lambda_result_map,
                                            result))
                semaphore.release()
            except Exception as e:
                print "Spoj lambda request error %s %s %s" % (problem_slug,
                                                              self.handle,
                                                              e)
                self.retrieval_failure = SERVER_FAILURE

        all_problem_names = _get_problem_names(response_text)

        for i in xrange(0, len(all_problem_names), AWS_LAMBDA_CONCURRENCY):
            # Parallely send requests of batch size AWS_LAMBDA_CONCURRENCY

            # If the previous batch failed, don't process any further
            if self.retrieval_failure is not None:
                return
            threads = []
            batch = all_problem_names[i : i + AWS_LAMBDA_CONCURRENCY]
            semaphore = BoundedSemaphore(len(batch))
            for problem_slug in batch:
                threads.append(gevent.spawn(_get_problem_wise_submissions,
                                            semaphore,
                                            problem_slug))
            gevent.joinall(threads)
            time.sleep(1)

    # -------------------------------------------------------------------------
    def get_submissions(self, last_retrieved, is_daily_retrieval):
        """
            Retrieve Spoj submissions after last retrieved timestamp

            @param last_retrieved (DateTime): Last retrieved timestamp for the user
            @return (List): List of submissions containing all the
                            information
        """

        handle = self.handle
        self.is_daily_retrieval = is_daily_retrieval
        self.submissions = []
        str_init_time = time.strptime(str(current.INITIAL_DATE),
                                      "%Y-%m-%d %H:%M:%S")
        # Test for invalid handles
        if  last_retrieved == str_init_time:
            url = current.SITES[self.site] + "users/" + handle
            first_response = get_request(url,
                                         timeout=10,
                                         is_daily_retrieval=self.is_daily_retrieval)

            if first_response in REQUEST_FAILURES:
                return first_response

            # Bad but correct way of checking if the handle exists
            if first_response.text.find("History of submissions") == -1:
                return NOT_FOUND

        if current.environment == "production" and \
           last_retrieved == str_init_time:
            # Call this only for production environment when the user's initial
            # date is current.INITIAL_DATE
            self.new_submission_retrieval(str(current.INITIAL_DATE),
                                          first_response.text)
        else:
            self.old_submission_retrieval(last_retrieved)

        if self.retrieval_failure is not None:
            return self.retrieval_failure
        else:
            return self.submissions

# =============================================================================
