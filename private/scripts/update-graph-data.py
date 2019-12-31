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
import sites as all_site_profiles
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
user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36"

# ==============================================================================
def log_line(message):
    print str(datetime.now()) + " " + message

# ==============================================================================
class User:

    # --------------------------------------------------------------------------
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
        # To track one of the retrieval failed with server failure
        # so that it can be re-tried
        self.retrieval_failed = False

        if os.path.exists(self.pickle_file_path):
            self.previous_graph_data = pickle.load(open(self.pickle_file_path, "rb"))
            self.graph_data = dict(self.previous_graph_data)
            for site_data in self.previous_graph_data:
                for contest_data in self.previous_graph_data[site_data]:
                    self.contest_mapping[contest_data["title"]] = contest_data["data"]

    # --------------------------------------------------------------------------
    def get_debug_statement(self):
        return "%s(%s)%s:" % (self.user_record.stopstalk_handle,
                              self.user_record.id,
                              " CUS" if self.custom else "")

    # --------------------------------------------------------------------------
    def fetch_site_rating_history(self, site):
        handle = self.handles[site + "_handle"]
        try:
            get_rating_func = getattr(all_site_profiles, site).Profile.rating_graph_data
        except AttributeError:
            # The profile site does not support fetching rating graph data
            log_line(site + " rating history not implemented")
            return
        result = get_rating_func(handle)

        if result in REQUEST_FAILURES:
            if result != NOT_FOUND:
                self.retrieval_failed = True
            log_line("%s Request ERROR: %s %s %s" % (self.get_debug_statement(), site, handle, result))
            return

        self.graph_data[site + "_data"] = result

    # --------------------------------------------------------------------------
    def write_to_filesystem(self):
        if self.previous_graph_data == self.graph_data:
            log_line(self.get_debug_statement() + "No update in graph data")
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

        log_line(self.get_debug_statement() + "Writing to filesystem done")

    # --------------------------------------------------------------------------
    def update_graph_data(self, sites):
        threads = []
        for site in sites:
            if self.handles.has_key(site + "_handle") and self.handles[site + "_handle"] != "":
                threads.append(gevent.spawn(getattr(self,
                                                    "fetch_site_rating_history"),
                                            site))

        gevent.joinall(threads)
        if self.retrieval_failed == False:
            current.REDIS_CLIENT.delete("get_stopstalk_rating_history_" + self.user_record.stopstalk_handle)
            self.write_to_filesystem()
            self.user_record.update_record(graph_data_retrieved=True)
        else:
            log_line(self.get_debug_statement() + "Writing to file skipped")

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

# ==============================================================================
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
        log_line("Invalid Arguments")

    for user_object in user_objects:
        user_object.update_graph_data(sites)

    if getuser() == "root":
        dir_stats = os.stat(DIR_PATH)
        www_data = getpwnam("www-data")
        if dir_stats.st_uid != www_data.pw_uid or \
           dir_stats.st_gid != www_data.pw_gid:
            log_line("Changing user and group for " + " " + DIR_PATH)
            os.chown(DIR_PATH, www_data.pw_uid, www_data.pw_gid)
