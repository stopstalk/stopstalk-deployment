import bs4
import time
import datetime
import json
import requests

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

    for page in range(10):
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

def lambda_handler(request):
    print("Executing for", request.args)
    spoj_handle = request.args.get("spoj_handle")
    problem_slug = request.args.get("problem_slug")
    last_retrieved = request.args.get("last_retrieved")
    submissions = get_problem_wise_submissions(spoj_handle, problem_slug, last_retrieved)

    return json.dumps(submissions)
