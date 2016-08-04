import requests
import re
import json
import gevent
from gevent import monkey
gevent.monkey.patch_all(thread=False)

from bs4 import BeautifulSoup
from datetime import datetime, timedelta

def get_request(url):
    i = 0
    while i < 5:
        try:
            response = requests.get(url,
                                    proxies={"http": "http://proxy.iiit.ac.in:8080"})
        except Exception as e:
            print e
            return -1

        if response.status_code == 200:
            return response
        elif response.status_code == 404:
            print 404,
            return -1
        i += 1

    return -1

class User:

    def __init__(self, handles):
        self.handles = handles
        self.graph_data = {}

    def codechef_data(self):
        handle = self.handles["codechef_handle"]
        url = "https://www.codechef.com/users/" + handle
        response = get_request(url)
        if response == -1:
            print "Request ERROR: CodeChef " + url
            return

        def zero_pad(string):
            return "0" + string if len(string) == 1 else string

        soup = BeautifulSoup(response.text)
        script = str(soup.find_all("script")[33])
        data = re.findall(r"\[.*?\]", script)

        months = {"Jan": ["January", "JAN"],
                  "Feb": ["February", "FEB"],
                  "Mar": ["March", "MARCH"],
                  "Apr": ["April", "APRIL"],
                  "May": ["May", "MAY"],
                  "Jun": ["June", "JUNE"],
                  "Jul": ["July", "JULY"],
                  "Aug": ["August", "AUG"],
                  "Sep": ["September", "SEPT"],
                  "Oct": ["October", "OCT"],
                  "Nov": ["November", "NOV"],
                  "Dec": ["December", "DEC"]}

        if len(data) < 2:
            print "Cannot find CodeChef user " + handle
            return

        long_ratings = eval(data[1])
        long_months = eval(data[3])
        short_ratings = eval(data[5])
        short_months = eval(data[7])

        long_contest_data = {}
        for i in xrange(len(long_ratings)):
            month, year = long_months[i].split("/")
            year = zero_pad(year)
            time_stamp = str(datetime.strptime(month + " " + year, "%b %y"))
            contest_name = "%s Long Challenge 20%s" % (months[month][0], year)
            contest_url = "https://www.codechef.com/" + months[month][1] + year
            long_contest_data[time_stamp] = {"name": contest_name,
                                             "url": contest_url,
                                             "rating": long_ratings[i]}

        short_contest_data = {}
        contest_iterator = -1
        flag = False

        for i in xrange(len(short_ratings)):
            month, year = short_months[i].split("/")
            year = zero_pad(year)
            time_stamp = str(datetime.strptime(month + " " + year, "%b %y"))
            contest_name = "%s Cook off 20%s" % (months[month][0], year)
            contest_iterator += 1
            if contest_iterator == 0:
                # June'10 Cook off has a different URL
                contest_url = "https://www.codechef.com/JUNE10"
            elif contest_iterator == 3 and flag == False:
                # Sept'10 Cook off has a different URL
                contest_url = "https://www.codechef.com/SEPT10"
                contest_iterator -= 1
                flag = True
            else:
                contest_url = "https://www.codechef.com/COOK%s" % zero_pad(str(contest_iterator))
            short_contest_data[time_stamp] = {"name": contest_name,
                                              "url": contest_url,
                                              "rating": short_ratings[i]}

        self.graph_data["codechef_data"] = {1: {"title": "CodeChef Long",
                                                "data": long_contest_data},
                                            2: {"title": "CodeChef Cook off",
                                                "data": short_contest_data}}

    def codeforces_data(self):
        handle = self.handles["codeforces_handle"]
        website = "http://codeforces.com/"
        url = "%sapi/contest.list" % website
        response = get_request(url)
        if response == -1:
            print "Request ERROR: Codeforces " + url
            return

        contest_list = response.json()["result"]
        all_contests = {}

        for contest in contest_list:
            all_contests[contest["id"]] = contest

        url = "%scontests/with/%s" % (website, handle)

        response = get_request(url)
        if response == -1:
            print "Request ERROR: Codeforces " + url
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
            rank = int(all_tds[2].find("a").contents[0].strip())
            solved_count = int(all_tds[3].find("a").contents[0].strip())
            rating_change = int(all_tds[4].find("span").contents[0].strip())
            new_rating = int(all_tds[5].contents[0].strip())
            contest = all_contests[contest_id]
            time_stamp = str(datetime.fromtimestamp(contest["startTimeSeconds"]))
            contest_data[time_stamp] = {"name": contest["name"],
                                        "url": "%scontest/%d" % (website,
                                                                 contest_id),
                                        "rating": new_rating,
                                        "ratingChange": rating_change,
                                        "rank": rank,
                                        "solvedCount": solved_count}

        self.graph_data["codeforces_data"] = {1: {"title": "Codeforces",
                                                  "data": contest_data}}

    def hackerrank_data(self):
        handle = self.handles["hackerrank_handle"]
        website = "https://www.hackerrank.com/"
        url = "%srest/hackers/%s/rating_histories2" % (website, handle)
        response = get_request(url)
        if response == -1:
            print "Request ERROR: Hackerrank " + url
            return
        response = response.json()["models"]

        hackerrank_graphs = {}
        graph_count = 1
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
                                          "rating": contest["rating"],
                                          "rank": contest["rank"]}

            graph_name = "HackerRank - %s" % contest_class["category"]
            hackerrank_graphs[graph_count] = {"title": graph_name,
                                              "data": final_json}
            graph_count += 1

        self.graph_data["hackerrank_data"] = hackerrank_graphs

    def spoj_data(self):
        pass

    def hackerearth_data(self):
        pass

    def write_to_db(self, user_id, custom):
        gdtable = db.graph_data
        if custom:
            gdtable.update_or_insert(gdtable.custom_user_id==user_id,
                                     custom_user_id=user_id,
                                     **self.graph_data)
        else:
            gdtable.update_or_insert(gdtable.user_id==user_id,
                                     user_id=user_id,
                                     **self.graph_data)
        print "Writing to db done"

    def get_graph_data(self, user_id, custom=False):
        threads = []
        for site in current.SITES:
            if self.handles.has_key(site.lower() + "_handle"):
                threads.append(gevent.spawn(getattr(self,
                                                    site.lower() + "_data")))

        gevent.joinall(threads)
        self.write_to_db(user_id, custom)

if __name__ == "__main__":

    db = current.db
    atable = db.auth_user
    cftable = db.custom_friend
    users = db(atable).select()
    custom_users = db(cftable).select()

    def get_user_data(list_of_users, custom=False):
        for user in list_of_users:
            handles = {}
            print "Updating for " + user.stopstalk_handle
            for site in current.SITES:
                site_handle = site.lower() + "_handle"
                if user[site_handle]:
                    handles[site_handle] = user[site_handle]
            user_class = User(handles)
            user_class.get_graph_data(user.id, custom=custom)

    get_user_data(users)
    get_user_data(custom_users, True)
