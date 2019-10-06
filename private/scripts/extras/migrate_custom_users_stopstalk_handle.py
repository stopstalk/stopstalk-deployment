"""
    Copyright (c) 2015-2019 Raj Patel(raj454raj@gmail.com), StopStalk

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

import time

cftable = db.custom_friend
stable = db.submission

custom_friends = db(cftable).select()
custom_handles = [x.stopstalk_handle for x in custom_friends]

for handle in custom_handles:
    keys_for_handle = current.REDIS_CLIENT.keys("*" + handle)
    print handle, keys_for_handle
    for key in keys_for_handle:
        current.REDIS_CLIENT.delete(key)

for custom_friend in custom_friends:
    new_stopstalk_handle = "cus_" + custom_friend.stopstalk_handle
    row_count = db(stable.custom_user_id == custom_friend.id).update(stopstalk_handle=new_stopstalk_handle)
    print custom_friend.id, "updated", row_count, "submission records"
    custom_friend.update_record(stopstalk_handle=new_stopstalk_handle)
    db.commit()
