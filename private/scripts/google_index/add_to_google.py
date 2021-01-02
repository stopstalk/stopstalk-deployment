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

# Wrote when was tooooo sleepy, don't judge the DRYness :/

from oauth2client.service_account import ServiceAccountCredentials
import httplib2
import datetime
import time
import sys

def log_info(message):
    print "%s: %s" % (str(datetime.datetime.now()),
                      message)

def getHTTPObject():
    SCOPES = [ "https://www.googleapis.com/auth/indexing" ]

    # service_account_file.json is the private key that you created for your service account.
    google_index_dir = "/home/www-data/web2py/applications/stopstalk/private/scripts/google_index"
    # google_index_dir = "/Users/raj454raj/devwork/stopstalk/web2py/applications/stopstalk/private/scripts/google_index"
    JSON_KEY_FILE = "%s/service-account.json" % google_index_dir

    credentials = ServiceAccountCredentials.from_json_keyfile_name(JSON_KEY_FILE, scopes=SCOPES)
    return credentials.authorize(httplib2.Http())

def make_api_request(url):
    content = "{\"url\": \"%s\", \"type\": \"URL_UPDATED\"}" % url
    http = getHTTPObject()
    ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"
    response, content = http.request(ENDPOINT, method="POST", body=content)
    log_info("API response - %s %s" % (str(response["status"]), url))
    return str(response["status"]) == "200"


TOTAL_REQUEST_CALLS = 900 # We have quota for 1000
current_request_count = {"users": 0, "problems": 0, "total": 0}

atable = db.auth_user
ptable = db.problem

# ===================
# Add users to Google
# ===================
last_user_id = current.REDIS_CLIENT.get("last_user_id_submitted_to_google")
last_user_id = 0 if last_user_id is None else int(last_user_id)

query = (atable.blacklisted == False) & \
        (atable.registration_key == "") & \
        (atable.id > last_user_id)
rows = db(query).select(atable.id,
                        atable.stopstalk_handle,
                        orderby=~atable.id,
                        limitby=(0, 300))

for row in rows:
    url = "https://www.stopstalk.com/user/profile/%s" % row.stopstalk_handle
    result = make_api_request(url)
    current_request_count["users"] += 1
    current_request_count["total"] += 1
    last_user_id = row.id
    if not result or current_request_count["total"] >= TOTAL_REQUEST_CALLS:
        log_info("Total requests for the day processed %s" % str(current_request_count))
        current.REDIS_CLIENT.set("last_user_id_submitted_to_google", row.id)
        sys.exit(0)
    time.sleep(1)

current.REDIS_CLIENT.set("last_user_id_submitted_to_google", last_user_id)

last_problem_id = current.REDIS_CLIENT.get("last_problem_id_submitted_to_google")
last_problem_id = 0 if last_problem_id is None else int(last_problem_id)

query = (ptable.id > last_problem_id)
pids = db(query).select(ptable.id,
                        limitby=(0, 1000))
pids = [x.id for x in pids]

for pid in pids:
    url = "https://www.stopstalk.com/problems?problem_id=%d" % pid
    result = make_api_request(url)
    current_request_count["problems"] += 1
    current_request_count["total"] += 1
    last_problem_id = pid
    if not result or current_request_count["total"] >= TOTAL_REQUEST_CALLS:
        log_info("Total requests for the day processed %s" % str(current_request_count))
        current.REDIS_CLIENT.set("last_problem_id_submitted_to_google", pid)
        sys.exit(0)
    time.sleep(1)

current.REDIS_CLIENT.set("last_problem_id_submitted_to_google", last_problem_id)
log_info("Outside of both loops %s" % str(current_request_count))
