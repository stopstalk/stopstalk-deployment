# -*- coding: utf-8 -*-
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

import utilities
import requests
from prettytable import PrettyTable
from bs4 import BeautifulSoup

stopstalk_handle = "lebron"
custom = False

atable = db.auth_user

category_counts_dict = {}


user_record = db(atable.stopstalk_handle == stopstalk_handle).select().first()
user_id = user_record.id

# =============================================================================
solved_problems, unsolved_problems = utilities.get_solved_problems(user_id, custom)

solved_category_counts, unsolved_category_counts = utilities.get_category_wise_problems(solved_problems, unsolved_problems, set(), set())

problem_counts_table = PrettyTable()
problem_counts_table.field_names = ["Field", "Count"]
problem_counts_table.add_row(["Solved problem count", len(solved_problems)])
problem_counts_table.add_row(["Unsolved problem count", len(unsolved_problems)])
problem_counts_table.add_row(["Total problem count", len(solved_problems) + len(unsolved_problems)])

print problem_counts_table.get_string()
print

# =============================================================================
def populate_category_counts_dict(category, solved, count):
    if category not in category_counts_dict:
        category_counts_dict[category] = {"solved": 0, "unsolved": 0}

    category_counts_dict[category]["solved" if solved else "unsolved"] = count

for category in solved_category_counts:
    populate_category_counts_dict(category, True, len(solved_category_counts[category]))

for category in unsolved_category_counts:
    populate_category_counts_dict(category, False, len(unsolved_category_counts[category]))

category_counts_table = PrettyTable()
category_counts_table.field_names = ["Category", "Solved", "Unsolved"]

for category in category_counts_dict:
    category_counts_table.add_row([category, category_counts_dict[category]["solved"], category_counts_dict[category]["unsolved"]])

print category_counts_table.get_string()
print

# =============================================================================
contest_participation_table = PrettyTable()
contest_participation_table.field_names = ["Contest", "Count"]
contest_data = utilities.get_contest_graph_data(user_id, custom)["graphs"]

for contest in contest_data:
    contest_participation_table.add_row([contest["title"], len(contest["data"])])

print contest_participation_table.get_string()
print

# =============================================================================
def get_codeforces_rating(handle):
    response = requests.get("https://codeforces.com/api/user.info?handles=" + handle)
    response = response.json()
    # import ast
    # response = ast.literal_eval(response.text)
    return response["result"][0]["rating"], response["result"][0]["maxRating"]

def get_codechef_rating(handle):
    api_key = current.REDIS_CLIENT.get("codechef_access_token")
    response = requests.get("https://api.codechef.com/users/" + handle + "?fields=ratings,rankings",
                            headers={"Authorization": "Bearer " + api_key})
    response = response.json()
    return dict(global_ranking=response["result"]["data"]["content"]["rankings"]["allContestRanking"]["global"],
                country_ranking=response["result"]["data"]["content"]["rankings"]["allContestRanking"]["country"],
                rating=response["result"]["data"]["content"]["ratings"]["allContest"])

def get_atcoder_rating(handle):
    response = requests.get("https://atcoder.jp/users/" + handle)
    soup = BeautifulSoup(response.text, "lxml")
    try:
        contest_status_h3 = soup.find_all("h3")[-1]
    except:
        return None
    if contest_status_h3.text != "Contest Status":
        return "Something went wrong"

    contest_status_table = None
    for sibling in contest_status_h3.next_siblings:
        if sibling.name == "table":
            contest_status_table = sibling
            break

    def _get_digits(full_string):
        return "".join(c for c in full_string.strip().split()[0] if c.isdigit())

    tds = contest_status_table.find_all("td")
    rank = _get_digits(tds[0].text)
    rating = _get_digits(tds[1].text)
    max_rating = _get_digits(tds[2].text)
    return rating, max_rating, rank

def get_hackerrank_rating(handle):
    response = requests.get("https://www.hackerrank.com/rest/hackers/%s/scores_elo" % handle,
                            headers={"User-Agent": COMMON_USER_AGENT})
    response = response.json()
    for contest in response:
        if contest["name"] == "Algorithms":
            return contest["contest"]["score"], contest["contest"]["rank"]
    return None

contest_rating_table = PrettyTable()

contest_rating_table.field_names = ["Site", "Rating", "Global rank", "Country rank"]

# if user_record.codechef_handle != "":
#     codechef_data = get_codechef_rating(user_record.codechef_handle)
#     contest_rating_table.add_row(["CodeChef", codechef_data["rating"], codechef_data["global_ranking"], codechef_data["country_ranking"]])

if user_record.codeforces_handle != "":
    codeforces_data = get_codeforces_rating(user_record.codeforces_handle)
    contest_rating_table.add_row(["Codeforces", "%d (Max: %d)" % (codeforces_data[0], codeforces_data[1]), "", ""])

if user_record.atcoder_handle != "":
    atcoder_data = get_atcoder_rating(user_record.codeforces_handle)
    if atcoder_data is not None:
        contest_rating_table.add_row(["AtCoder", "%s (Max: %s)" % (atcoder_data[0], atcoder_data[1]), atcoder_data[2], ""])

if user_record.hackerrank_handle != "":
    hackerrank_data = get_hackerrank_rating(user_record.hackerrank_handle)
    contest_rating_table.add_row(["HackerRank", hackerrank_data[0], hackerrank_data[1], ""])
print contest_rating_table.get_string()
