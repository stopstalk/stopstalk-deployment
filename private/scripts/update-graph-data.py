"""
    Copyright (c) 2015-2018 Raj Patel(raj454raj@gmail.com), StopStalk

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

# Usage
# -----
# First Argument - Comma seperated lower-cased sites
# Second Argument - {batch, specific_user, new_user}
#   * batch - Update graph data for users for whom (user_id % <fourth_argment> == <third_argument>)
#   * specific_user -
#       Third argument - normal/custom
#       Fourth argument - <user_id>
#   * new_user - Retrieve contest data for all the users whose graph_data_retrieved is not True
# python web2py.py -S stopstalk -M -R applications/stopstalk/private/scripts/update-graph-data.py -A codechef,codeforces,hackerrank,hackerearth batch 5 100

import requests, re, os, sys, json, gevent, pickle
from getpass import getuser
from pwd import getpwnam
from gevent import monkey
gevent.monkey.patch_all(thread=False)

from bs4 import BeautifulSoup
from datetime import datetime, timedelta

atable = db.auth_user
cftable = db.custom_friend

# Constants to be used in case of request failures
SERVER_FAILURE = "SERVER_FAILURE"
NOT_FOUND = "NOT_FOUND"
OTHER_FAILURE = "OTHER_FAILURE"
REQUEST_FAILURES = (SERVER_FAILURE, NOT_FOUND, OTHER_FAILURE)
INVALID_HANDLES = set([(row.handle, row.site.lower()) for row in db(db.invalid_handle).select()])
DIR_PATH = "./applications/stopstalk/graph_data/"

# -----------------------------------------------------------------------------
def get_request(url, headers={}, timeout=current.TIMEOUT, params={}):
    """
        Make a HTTP GET request to a url

        @param url (String): URL to make get request to
        @param headers (Dict): Headers to be passed along
                               with the request headers

        @return: Response object or -1 or {}
    """

    i = 0
    while i < current.MAX_TRIES_ALLOWED:
        try:
            response = requests.get(url,
                                    headers=headers,
                                    params=params,
                                    proxies=current.PROXY,
                                    timeout=timeout)
        except Exception as e:
            print e, url
            return SERVER_FAILURE

        if response.status_code == 200:
            return response
        elif response.status_code == 404 or response.status_code == 400:
            # User not found
            # 400 for CodeForces users
            return NOT_FOUND
        i += 1

    # Request unsuccessful even after MAX_TRIES_ALLOWED
    return OTHER_FAILURE

class User:

    def __init__(self, user_id, handles, user_record, custom=False):
        self.handles = handles
        self.custom = custom
        self.pickle_file_path = DIR_PATH + str(user_id) + ".pickle"
        if custom:
            self.pickle_file_path = self.pickle_file_path.replace(".pickle", "_custom.pickle")

        self.contest_mapping = {}
        self.previous_graph_data = None
        self.graph_data = dict([(x.lower() + "_data", []) for x in current.SITES])
        self.user_record = user_record

        if os.path.exists(self.pickle_file_path):
            self.previous_graph_data = pickle.load(open(self.pickle_file_path, "rb"))
            self.graph_data = dict(self.previous_graph_data)
            for site_data in self.previous_graph_data:
                for contest_data in self.previous_graph_data[site_data]:
                    self.contest_mapping[contest_data["title"]] = contest_data["data"]

    def get_debug_statement(self):
        return "%s(%s)%s:" % (self.user_record.stopstalk_handle,
                              self.user_record.id,
                              " CUS" if self.custom else "")

    def codechef_data(self):
        handle = self.handles["codechef_handle"]
        url = "https://www.codechef.com/users/" + handle
        response = get_request(url)
        if response in REQUEST_FAILURES:
            print "Request ERROR: CodeChef " + url + " " + response
            return

        def zero_pad(string):
            return "0" + string if len(string) == 1 else string

        try:
            ratings = eval(re.search("var all_rating = .*?;", response.text).group()[17:-1])
        except Exception as e:
            print e
            return

        long_contest_data = {}
        cookoff_contest_data = {}
        ltime_contest_data = {}

        for contest in ratings:
            this_obj = None
            if contest["code"].__contains__("COOK"):
                # Cook off contest
                this_obj = cookoff_contest_data
            elif contest["code"].__contains__("LTIME"):
                # Lunchtime contest
                this_obj = ltime_contest_data
            else:
                # Long contest
                this_obj = long_contest_data
            # getdate, getmonth and getyear give end_date only
            time_stamp = str(datetime.strptime(contest["end_date"], "%Y-%m-%d %H:%M:%S"))
            this_obj[time_stamp] = {"name": contest["name"],
                                    "url": "https://www.codechef.com/" + contest["code"],
                                    "rating": str(contest["rating"]),
                                    "rank": contest["rank"]}

        self.graph_data["codechef_data"] = [{"title": "CodeChef Long",
                                             "data": long_contest_data},
                                            {"title": "CodeChef Cook-off",
                                             "data": cookoff_contest_data},
                                            {"title": "CodeChef Lunchtime",
                                             "data": ltime_contest_data}]

    def codeforces_data(self):
        handle = self.handles["codeforces_handle"]
        website = "http://codeforces.com/"
        url = "%sapi/contest.list" % website
        response = get_request(url)
        if response in REQUEST_FAILURES:
            print "Request ERROR: Codeforces " + url + " " + response
            return

        contest_list = response.json()["result"]
        all_contests = {}

        for contest in contest_list:
            all_contests[contest["id"]] = contest

        url = "%scontests/with/%s" % (website, handle)

        response = get_request(url)
        if response in REQUEST_FAILURES:
            print "Request ERROR: Codeforces " + url + " " + response
            return

        soup = BeautifulSoup(response.text, "lxml")
        try:
            tbody = soup.find("table", class_="tablesorter").find("tbody")
        except AttributeError:
            print "Cannot find CodeForces user " + handle
            return

        contest_data = {}
        for tr in tbody.find_all("tr"):
            all_tds = tr.find_all("td")
            contest_id = int(all_tds[1].find("a")["href"].split("/")[-1])
            if all_tds[2].find("a"):
                # For some users there is no rank for some contests
                # Example http://codeforces.com/contests/with/cjoa (Contest number 3)
                rank = int(all_tds[2].find("a").contents[0].strip())
            else:
                # @Todo: Will this create any issues as rank is assumed to be an int
                rank = ""
            solved_count = int(all_tds[3].find("a").contents[0].strip())
            rating_change = int(all_tds[4].find("span").contents[0].strip())
            new_rating = int(all_tds[5].contents[0].strip())
            contest = all_contests[contest_id]
            time_stamp = str(datetime.fromtimestamp(contest["startTimeSeconds"]))
            contest_data[time_stamp] = {"name": contest["name"],
                                        "url": "%scontest/%d" % (website,
                                                                 contest_id),
                                        "rating": str(new_rating),
                                        "ratingChange": rating_change,
                                        "rank": rank,
                                        "solvedCount": solved_count}

        self.graph_data["codeforces_data"] = [{"title": "Codeforces",
                                               "data": contest_data}]

    def hackerrank_data(self):
        handle = self.handles["hackerrank_handle"]
        website = "https://www.hackerrank.com/"
        url = "%srest/hackers/%s/rating_histories_elo" % (website, handle)
        response = get_request(url)
        if response in REQUEST_FAILURES:
            print "Request ERROR: HackerRank " + url + " " + response
            return
        response = response.json()["models"]

        hackerrank_graphs = []
        for contest_class in response:
            final_json = {}
            for contest in contest_class["events"]:
                time_stamp = contest["date"][:-5].split("T")
                time_stamp = datetime.strptime(time_stamp[0] + " " + time_stamp[1],
                                               "%Y-%m-%d %H:%M:%S")
                # Convert UTC to IST
                time_stamp += timedelta(hours=5, minutes=30)
                time_stamp = str(time_stamp)
                final_json[time_stamp] = {"name": contest["contest_name"],
                                          "url": website + contest["contest_slug"],
                                          "rating": str(contest["rating"]),
                                          "rank": contest["rank"]}

            graph_name = "HackerRank - %s" % contest_class["category"]
            hackerrank_graphs.append({"title": graph_name,
                                      "data": final_json})

        self.graph_data["hackerrank_data"] = hackerrank_graphs

    def spoj_data(self):
        pass

    def hackerearth_data(self):
        url = "https://www.hackerearth.com/ratings/AJAX/rating-graph/" + \
              self.handles["hackerearth_handle"]
        response = get_request(url)
        if response in REQUEST_FAILURES:
            print "Request ERROR: HackerEarth " + url + " " + response
            return
        if response.text == "":
            print "Request ERROR: HackerEarth " + url + " " + NOT_FOUND
            return
        contest_data = eval(re.findall(r"var dataset = \[.*?\]", response.text)[0][14:])
        if len(contest_data) == 0:
            return

        hackerearth_data = {}
        for contest in contest_data:
            time_stamp = str(datetime.strptime(contest["event_start"], "%d %b %Y, %I:%M %p"))
            url = "https://www.hackerearth.com" + contest["event_url"]
            hackerearth_data[time_stamp] = {"name": contest["event_title"],
                                            "rating": contest["rating"],
                                            "url": url,
                                            "rank": contest["rank"]}
        self.graph_data["hackerearth_data"] = [{"title": "HackerEarth",
                                                "data": hackerearth_data}]

    def uva_data(self):
        pass

    def write_to_filesystem(self):
        if self.previous_graph_data == self.graph_data:
            print "No update in graph data"
            return

        if self.previous_graph_data is not None:
            # Pickle file already exists for the user
            for site_data in self.graph_data:
                for contest_data in self.graph_data[site_data]:
                    try:
                        previous_value = self.contest_mapping[contest_data["title"]]
                    except KeyError:
                        continue
                    if len(contest_data["data"]) < len(previous_value):
                        contest_data = previous_value
        pickle.dump(self.graph_data, open(self.pickle_file_path, "wb"))

        if getuser() == "root":
            # For production machine as nginx runs with www-data
            # and it can't delete these files else
            www_data = getpwnam("www-data")
            os.chown(self.pickle_file_path, www_data.pw_uid, www_data.pw_gid)

        print "Writing to filesystem done"

    def update_graph_data(self, sites):
        threads = []
        for site in sites:
            if self.handles.has_key(site + "_handle") and self.handles[site + "_handle"] != "":
                threads.append(gevent.spawn(getattr(self,
                                                    site + "_data")))

        gevent.joinall(threads)
        self.write_to_filesystem()
        self.user_record.update_record(graph_data_retrieved=True)

def get_user_objects(aquery=None, cquery=None, sites=None):
    user_objects = []
    users = []
    if aquery:
        aquery &= (atable.registration_key == "") & \
                  (atable.blacklisted == False)
        users += db(aquery).select().records
    if cquery:
        users += db(cquery).select().records

    for user in users:
        this_user = None
        if "custom_friend" in user:
            custom = True
            this_user = user["custom_friend"]
        else:
            custom = False
            this_user = user["auth_user"]

        user_dict = {}
        for site in sites:
            site_handle = site + "_handle"
            if this_user[site_handle] != "" and \
               (this_user[site_handle], site) not in INVALID_HANDLES:
                user_dict[site_handle] = this_user[site_handle]
        user_objects.append(User(this_user.id, user_dict, this_user, custom))

    return user_objects

if __name__ == "__main__":
    sites = sys.argv[1].strip().split(",")
    user_objects = []

    if sys.argv[2] == "batch":
        index = int(sys.argv[3])
        N = int(sys.argv[4])
        user_objects = get_user_objects(aquery=(atable.id % N == index),
                                        cquery=(cftable.id % N == index),
                                        sites=sites)
    elif sys.argv[2] == "specific_user":
        if sys.argv[3] == "normal":
            user_objects = get_user_objects(aquery=(atable.id == int(sys.argv[4])),
                                            sites=sites)
        else:
            user_objects = get_user_objects(cquery=(cftable.id == int(sys.argv[4])),
                                            sites=sites)
    elif sys.argv[2] == "new_user":
        user_objects = get_user_objects(aquery=(atable.graph_data_retrieved != True),
                                        cquery=(cftable.graph_data_retrieved != True),
                                        sites=sites)
    else:
        print "Invalid Arguments"

    for user_object in user_objects:
        print user_object.get_debug_statement(),
        user_object.update_graph_data(sites)

    if getuser() == "root":
        dir_stats = os.stat(DIR_PATH)
        www_data = getpwnam("www-data")
        if dir_stats.st_uid != www_data.pw_uid or \
           dir_stats.st_gid != www_data.pw_gid:
            print "Changing user and group for", DIR_PATH
            os.chown(DIR_PATH, www_data.pw_uid, www_data.pw_gid)