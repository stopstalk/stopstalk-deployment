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
import time

SCOPES = [ "https://www.googleapis.com/auth/indexing" ]
ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"

# service_account_file.json is the private key that you created for your service account.
google_index_dir = "/home/www-data/web2py/applications/stopstalk/private/scripts/google_index"
# google_index_dir = "/Users/raj454raj/devwork/stopstalk/web2py/applications/stopstalk/private/scripts/google_index"
JSON_KEY_FILE = "%s/service-account.json" % google_index_dir

credentials = ServiceAccountCredentials.from_json_keyfile_name(JSON_KEY_FILE, scopes=SCOPES)
http = credentials.authorize(httplib2.Http())

last_user_id = current.REDIS_CLIENT.get("last_user_id_submitted_to_google")
last_user_id = 0 if last_user_id is None else int(last_user_id)

atable = db.auth_user
cftable = db.custom_friend
query = (atable.blacklisted == False) & \
        (atable.registration_key == "") & \
        (atable.id > last_user_id)
rows = db(query).select(orderby=~atable.id,
                        limitby=(0, 100))

if len(rows) > 0:
    current.REDIS_CLIENT.set("last_user_id_submitted_to_google",
                             rows.first().id)

for row in rows:
    url = "https://www.stopstalk.com/user/profile/%s" % row.stopstalk_handle
    content = "{\"url\": \"%s\", \"type\": \"URL_UPDATED\"}" % url

    response, content = http.request(ENDPOINT, method="POST", body=content)
    print response, content
    time.sleep(1)

last_custom_user_id = current.REDIS_CLIENT.get("last_custom_user_id_submitted_to_google")
last_custom_user_id = 0 if last_custom_user_id is None else int(last_custom_user_id)

rows = db(cftable.id > last_custom_user_id).select(orderby=~cftable.id,
                                                   limitby=(0, 50))
if len(rows) > 0:
    current.REDIS_CLIENT.set("last_custom_user_id_submitted_to_google",
                             rows.first().id)

for row in rows:
    url = "https://www.stopstalk.com/user/profile/%s" % row.stopstalk_handle
    content = "{\"url\": \"%s\", \"type\": \"URL_UPDATED\"}" % url

    response, content = http.request(ENDPOINT, method="POST", body=content)
    print response, content
    time.sleep(1)
