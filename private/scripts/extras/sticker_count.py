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
####################################################################
#         DEPRECATED AFTER ADDING `following` table
####################################################################

ftable = db.friends
atable = db.auth_user

all_users = db(atable).select(atable.id,
                              atable.stopstalk_handle,
                              atable.email)
for user in all_users:

    rows = db(ftable.user_id == user.id).select(ftable.friend_id)

    valid_friends = 0
    for row in rows:
        claimable = True
        thisfriend = row.friend_id
        name = thisfriend.first_name + " " + thisfriend.last_name
        claimable &= thisfriend.authentic

        query = (ftable.user_id == thisfriend)
        friends_of_friends = db(query).select(ftable.friend_id)
        institute_friends = 0
        for fof in friends_of_friends:
            if fof.friend_id.institute == thisfriend.institute and \
               fof.friend_id.institute != "Other":
                institute_friends += 1
        if institute_friends > 1:
            pass
        else:
            if institute_friends == 0:
                claimable &= False
            else:
                if len(friends_of_friends) >= 3:
                    claimable &= True
                else:
                    claimable &= False

        if claimable:
            valid_friends += 1

    print user.email, valid_friends / 3
