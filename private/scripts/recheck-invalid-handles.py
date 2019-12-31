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

import requests, bs4
import sites

# Constants to be used in case of request failures
SERVER_FAILURE = "SERVER_FAILURE"
NOT_FOUND = "NOT_FOUND"
OTHER_FAILURE = "OTHER_FAILURE"
REQUEST_FAILURES = (SERVER_FAILURE, NOT_FOUND, OTHER_FAILURE)

def get_invalid_handle_method(site):
    site_class = getattr(sites, site.lower())
    invalid_handle_method = getattr(site_class.Profile, "is_invalid_handle")
    return invalid_handle_method

if __name__ == "__main__":

    ihtable = db.invalid_handle
    atable = db.auth_user
    cftable = db.custom_friend
    stable = db.submission
    nrtable = db.next_retrieval
    mapping = {}
    handle_to_row = {}

    for site in current.SITES:
        mapping[site] = get_invalid_handle_method(site)
        handle_to_row[site] = {}

    impossiblehandle = "thisreallycantbeahandle308"
    assert(all(map(lambda site: get_invalid_handle_method(site)(impossiblehandle), current.SITES.keys())))

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

    update_dict = {"stopstalk_rating": 0,
                   "stopstalk_prev_rating": 0,
                   "per_day": 0.0,
                   "per_day_change": "0.0",
                   "authentic": False}

    final_delete_query = False
    cnt = 0
    for row in db(ihtable).iterselect():
        # If not an invalid handle anymore
        if handle_to_row[row.site].has_key(row.handle) and mapping[row.site](row.handle) is False:
            cnt += 1
            print row.site, row.handle, "deleted"
            for row_obj in handle_to_row[row.site][row.handle]:
                print "\t", row_obj.stopstalk_handle, "updated"
                update_dict[row.site.lower() + "_lr"] = current.INITIAL_DATE
                row_obj.update_record(**update_dict)
                if "user_id" in row_obj:
                    # Custom user
                    db(nrtable.custom_user_id == row_obj.id).update(**{row.site.lower() + "_delay": 0})
                else:
                    db(nrtable.user_id == row_obj.id).update(**{row.site.lower() + "_delay": 0})
                final_delete_query |= ((stable.site == row.site) & \
                                       (stable.stopstalk_handle == row_obj.stopstalk_handle))
                del update_dict[row.site.lower() + "_lr"]
            row.delete_record()
        if cnt >= 10:
            if final_delete_query:
                db(final_delete_query).delete()
            cnt = 0
            final_delete_query = False

    if final_delete_query:
        db(final_delete_query).delete()
