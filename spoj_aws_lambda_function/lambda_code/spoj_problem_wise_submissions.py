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

import requests
import bs4
import time
import datetime
import json

def get_problem_wise_submissions(spoj_handle, problem_slug, last_retrieved):
    """
        Given the spoj handle and the problem, get the spoj submissions made
        after the timestamp represented by last_retrieved

        @params spoj_handle (String): Spoj handle
        @params problem_slug (String): Unique problem identifier on Spoj
        @params last_retrieved (String): Last retrieved for the user

        @return (List): List of [time of submission, name, status, points, language]
    """
    submissions = []
    last_retrieved = time.strptime(str(last_retrieved), "%Y-%m-%d %H:%M:%S")

    previd = -1
    currid = 0

    for page in xrange(10):
        url = "https://www.spoj.com/status/%s,%s/start=%d" % (problem_slug,
                                                              spoj_handle,
                                                              page * 20)
        response = requests.get(url)
        soup = bs4.BeautifulSoup(response.text)
        table_body = soup.find("tbody")
        has_pagination = soup.find("ul", class_="pagination") is not None

        row = 0
        for tr in table_body:
            if not isinstance(tr, bs4.element.Tag):
                continue

            if row == 0:
                currid = tr.contents[1].contents[0]
                if currid == previd:
                    return submissions
                previd = currid

            row += 1

            # Time of submission
            tos = tr.contents[3].contents[1].contents[0]
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

            # Problem Status
            status = str(tr.contents[6])
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
                                tr.contents[5].contents[0].contents[0].strip(),
                                submission_status,
                                points,
                                tr.contents[12].contents[1].contents[0]))

        if not has_pagination:
            # The problem didn't have more than one page of submissions
            break

    return submissions

def lambda_handler(event, context):
    spoj_handle = event["queryStringParameters"]["spoj_handle"]
    problem_slug = event["queryStringParameters"]["problem_slug"]
    last_retrieved = event["queryStringParameters"]["last_retrieved"]
    submissions = get_problem_wise_submissions(spoj_handle, problem_slug, last_retrieved)

    return {
        "isBase64Encoded": False,
        "statusCode": 200,
        "body": json.dumps(submissions)
    }

# Normal function usage

if __name__ == "__main__":
    print lambda_handler({
        "queryStringParameters": {
            "spoj_handle": "pranjalr34",
            "problem_slug": "GSS1",
            "last_retrieved": "2013-01-01 00:00:00"
        }
    }, None)
