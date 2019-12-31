# -*- coding: utf-8 -*-
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

fwtable = db.following
ftable = db.friends
frtable = db.friend_requests

current_set = db(fwtable).select()
current_set = set([(x.user_id, x.follower_id) for x in current_set])

insert_count = 0
for row in db(frtable).select():
    if (row.to_h, row.from_h) not in current_set:
        insert_count += 1
        fwtable.insert(user_id=row.to_h, follower_id=row.from_h)

for row in db(ftable).select():
    if (row.user_id, row.friend_id) not in current_set:
        # Note: Here the ordering does not matter
        insert_count += 1
        fwtable.insert(user_id=row.user_id, follower_id=row.friend_id)

print "Friends table:", db(ftable).count()
print "Friend requests table:", db(frtable).count()
print "Following table:", db(fwtable).count()
print "Insert count:", insert_count
