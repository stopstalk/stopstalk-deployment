import requests
import bs4
import time, datetime

def get_problem_wise_submissions(spoj_handle, problem_slug, last_retrieved):
    submissions = []
    last_retrieved = time.strptime(str(last_retrieved), "%Y-%m-%d %H:%M:%S")

    previd = -1
    currid = 0

    for page in xrange(10):
        url = "https://www.spoj.com/status/%s,%s/start=%d" % (problem_slug,
                                                              spoj_handle,
                                                              page * 20)
        response = requests.get(url)
        soup = bs4.BeautifulSoup(response.text, "lxml")
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
            # if curr <= last_retrieved:
            #     return submissions

            # Problem Name/URL
            uri = tr.contents[5].contents[0]
            uri["href"] = "https://www.spoj.com" + uri["href"]
            problem_link = eval(repr(uri["href"]).replace("\\", ""))

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
                                problem_link,
                                uri.contents[0].strip(),
                                submission_status,
                                points,
                                tr.contents[12].contents[1].contents[0],
                                ""))

        if not has_pagination:
            # The problem didn't have more than one page of submissions
            break

    return submissions

def lambda_handler(event, context):
    spoj_handle = event["queryStringParameters"]["spoj_handle"]
    problem_slug = event["queryStringParameters"]["problem_slug"]
    last_retrieved = event["queryStringParameters"]["last_retrieved"]
    submissions = get_problem_wise_submissions(spoj_handle, problem_slug, last_retrieved)
    print len(submissions)

    return {
        "result": submissions
    }

if __name__ == "__main__":
    print lambda_handler({
        "queryStringParameters": {
            "spoj_handle": "pranjalr34",
            "problem_slug": "GSS1",
            "last_retrieved": "2013-01-01 00:00:00"
        }
    }, None)
