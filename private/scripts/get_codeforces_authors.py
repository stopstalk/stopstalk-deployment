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

import os
import sys
import json
import time
import utilities
from sites.init import *
from sites import codeforces

contest_to_authors = None
DIR_PATH = "./applications/stopstalk/problem_setters/"

# ------------------------------------------------------------------------------
def get_gym_problem_authors():
    """
        Get gym problem authors (this is directly from API)
    """
    global contest_to_authors

    response = get_request("https://codeforces.com/api/contest.list?gym=true",
                           timeout=10,
                           headers={"User-Agent": COMMON_USER_AGENT})
    if response in REQUEST_FAILURES:
        print "[get_gym_problem_authors]: Error while requesting API", response
        return

    response = response.json()
    if response["status"] != "OK":
        print "[get_gym_problem_authors]: status not OK", response

    for row in response["result"]:
        if row["id"] not in contest_to_authors["gym"] and \
           "preparedBy" in row:
            contest_to_authors["gym"][int(row["id"])] = [row["preparedBy"]]
    return

# ------------------------------------------------------------------------------
def get_normal_problem_authors():
    """
        Get normal problem authors (crawling contest pages on codeforces)
    """
    global contest_to_authors

    base_url = "https://codeforces.com/contests/page/"
    pagination_count = 10000
    i = 1
    while i <= pagination_count:
        url = base_url + str(i)
        response = get_request(url,
                               headers={"User-Agent": COMMON_USER_AGENT})
        if response in REQUEST_FAILURES:
            print "[get_normal_problem_authors]: Failure for url", url, response
            break

        soup = bs4.BeautifulSoup(response.text, "lxml")
        pagination_count = int(soup.find_all("span", class_="page-index")[-1].text)

        all_trs = soup.find_all("tr")
        for tr in all_trs:
            tds = tr.find_all("td")
            if len(tds) <= 1:
                continue

            try:
                contest_id = tr["data-contestid"]
            except Exception as e:
                continue

            temp_data = tds[1].text.strip()
            if temp_data == "":
                print "[get_normal_problem_authors]: No authors for", contest_id
                continue

            authors = temp_data.split("\n")
            contest_to_authors["normal"][contest_id] = authors

        time.sleep(2)
        i += 1
    return

# ------------------------------------------------------------------------------
def get_metadata_filename():
    return DIR_PATH + "codeforces_metadata.json"

# ------------------------------------------------------------------------------
def get_initial_authors():
    """
        Get already existing authors in the file system
    """
    global contest_to_authors

    default_value = {
        "normal": {},
        "gym": {}
    }
    contest_to_authors = default_value

    try:
        file_obj = open(get_metadata_filename(), "r")
    except IOError:
        return

    contest_to_authors = json.loads(file_obj.read())
    file_obj.close()

# ------------------------------------------------------------------------------
def write_authors_to_file():
    """
        Write contest to authors mapping to a file as well as redis
    """
    file_obj = open(get_metadata_filename(), "w")
    file_obj.write(json.dumps(contest_to_authors))
    file_obj.close()
    current.REDIS_CLIENT.set(CODEFORCES_PROBLEM_SETTERS_KEY, json.dumps(contest_to_authors))

if __name__ == "__main__":
    if codeforces.Profile.is_website_down():
        print "Codeforces is down for now"
        sys.exit(0)

    get_initial_authors()
    get_gym_problem_authors()
    get_normal_problem_authors()
    write_authors_to_file()
    print contest_to_authors