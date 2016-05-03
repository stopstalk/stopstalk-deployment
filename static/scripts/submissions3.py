"""
    Copyright (c) 2015-2016 Raj Patel(raj454raj@gmail.com), StopStalk

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

import traceback
from datetime import datetime
import utilities

# @ToDo: Make this generalised
N = 0

if __name__ == "__main__":

    atable = db.auth_user
    cftable = db.custom_friend

    columns = "(`user_id`, `custom_user_id`, `stopstalk_handle`, " + \
              "`site_handle`, `site`, `time_stamp`, `problem_name`," + \
              "`problem_link`, `lang`, `status`, `points`, `view_link`)"

    # Update the last retrieved of the user
    today = datetime.now()
    query = (atable.id % 3 == N) & (atable.blacklisted == False)
    registered_users = db(query).select()

    all_rows = []

    for record in registered_users:
        all_rows.extend(utilities.retrieve_submissions(record, False))

    db(query).update(last_retrieved=today)

    query = (cftable.id % 3 == N) & (cftable.duplicate_cu == None)
    custom_users = db(query).select()
    for record in custom_users:
        all_rows.extend(utilities.retrieve_submissions(record, True))

    db(query).update(last_retrieved=today)

    if len(all_rows) != 0:
        sql_query = """INSERT INTO `submission` """ + \
                    columns + """ VALUES """ + \
                    ",".join(all_rows) + """;"""
        try:
            db.executesql(sql_query)
        except:
            traceback.print_exc()
            print "Error in " + site + " BULK INSERT for " + handle

# END =========================================================================
