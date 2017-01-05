"""
    Copyright (c) 2015-2017 Raj Patel(raj454raj@gmail.com), StopStalk

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

# Constants to be used in case of request failures
SERVER_FAILURE = "SERVER_FAILURE"
NOT_FOUND = "NOT_FOUND"
OTHER_FAILURE = "OTHER_FAILURE"
REQUEST_FAILURES = (SERVER_FAILURE, NOT_FOUND, OTHER_FAILURE)

# -----------------------------------------------------------------------------
def get_request(url, headers={}, timeout=current.TIMEOUT):
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

def codechef_invalid(handle):
    response = get_request("https://www.codechef.com/users/" + handle)
    if (len(response.history) > 0 and \
        response.history[0].status_code == 302) or \
       (response in REQUEST_FAILURES): # Any other server failure
        # If user handle is invalid CodeChef
        # redirects to https://www.codechef.com
        return True
    elif response in REQUEST_FAILURES:
        return
    return False

def codeforces_invalid(handle):
    response = get_request("http://codeforces.com/api/user.status?handle=" + \
                           handle + "&from=1&count=2")
    if response in REQUEST_FAILURES:
        return True
    return False

def spoj_invalid(handle):
    response = get_request("https://www.spoj.com/users/" + handle)
    if response in REQUEST_FAILURES:
        return True
    # Bad but correct way of checking if the handle exists
    if response.text.find("History of submissions") == -1:
        return True
    return False

def hackerearth_invalid(handle):
    url = "https://www.hackerearth.com/submissions/" + handle
    response = get_request(url)
    if response in REQUEST_FAILURES:
        return True
    return False

def hackerrank_invalid(handle):
    url = "https://www.hackerrank.com/rest/hackers/" + \
          handle + \
          "/recent_challenges?offset=0&limit=2"
    response = get_request(url)
    if response in REQUEST_FAILURES:
        return True
    return False

def uva_invalid(handle):
    url = "http://uhunt.felix-halim.net/api/uname2uid/" + handle
    response = get_request(url)
    if response in (SERVER_FAILURE, OTHER_FAILURE) or response.text.strip() == "0":
        return True
    return False

if __name__ == "__main__":

    ihtable = db.invalid_handle
    atable = db.auth_user
    cftable = db.custom_friend
    stable = db.submission
    mapping = {}
    handle_to_row = {}

    for site in current.SITES:
        mapping[site] = globals()[site.lower() + "_invalid"]
        handle_to_row[site] = {}

    impossiblehandle = "thisreallycantbeahandle308"
    assert(codechef_invalid(impossiblehandle) and \
           codeforces_invalid(impossiblehandle) and \
           spoj_invalid(impossiblehandle) and \
           hackerrank_invalid(impossiblehandle) and \
           hackerearth_invalid(impossiblehandle) and \
           uva_invalid(impossiblehandle) == True)

    def populate_handle_to_row(table):
        for row in db(table).select():
            for site in current.SITES:
                site_handle = row[site.lower() + "_handle"]
                if site_handle:
                    if handle_to_row[site].has_key(site_handle):
                        handle_to_row[site][site_handle].append(row)
                    else:
                        handle_to_row[site][site_handle] = [row]
    populate_handle_to_row(atable)
    populate_handle_to_row(cftable)

#    for site in current.SITES:
#        print site
#        for site_handle in handle_to_row[site]:
#            print "\t", site_handle
#            for row in handle_to_row[site][site_handle]:
#                print "\t\t", row.first_name, row.last_name, row.stopstalk_handle

    update_dict = {"rating": 0,
                   "prev_rating": 0,
                   "per_day": 0.0,
                   "per_day_change": "0.0",
                   "authentic": False}

    final_delete_query = False
    for row in db(ihtable).select():
        print "Processing", row.handle, row.site
        # If not an invalid handle anymore
        if handle_to_row[row.site].has_key(row.handle) and mapping[row.site](row.handle) is False:
            print "\t", row.site, row.handle, "deleted"
            for row_obj in handle_to_row[row.site][row.handle]:
                print "\t\t", row_obj.stopstalk_handle, "updated"
                update_dict[row.site.lower() + "_lr"] = current.INITIAL_DATE
                row_obj.update_record(**update_dict)
                final_delete_query |= ((stable.site == row.site) & \
                                       (stable.stopstalk_handle == row_obj.stopstalk_handle))
                del update_dict[row.site.lower() + "_lr"]
            row.delete_record()

    if final_delete_query:
        db(final_delete_query).delete()