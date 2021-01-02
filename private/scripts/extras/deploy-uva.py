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

import datetime

uhtable = db.uva_handles
atable = db.auth_user
cftable = db.custom_friend
uptable = uvadb.problem
uitable = uvadb.usernametoid

uva_handles = db(uhtable).select()
uva_handles = dict([(x.user_id, x.handle) for x in uva_handles])

users = db(atable).select()
for record in users:
    if uva_handles.has_key(record.id):
        record.update_record(uva_handle=uva_handles[record.id],
                             uva_lr=current.INITIAL_DATE,
                             rating=0,
                             prev_rating=0,
                             per_day=0.0,
                             per_day_change="0.0",
                             authentic=False)
    else:
        record.update_record(uva_handle="",
                             uva_lr=datetime.datetime.now())

custom_users = db(cftable).select()
for record in custom_users:
    record.update_record(uva_handle="",
                         uva_lr=datetime.datetime.now())
