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


"""
This should be executed before per-day update to consider the minor edge case
when a user register's and has duplicates and per-day is computed based on that
while after we will delete the duplicates which will lead to negative per-day change
"""
import datetime
stable = db.submission

right_now = datetime.datetime.now()
start_time = str(right_now - datetime.timedelta(days=5))[:-7]
end_time = str(right_now)[:-7]
print "Start time:", start_time, ", End time:", end_time
print "Starting query", datetime.datetime.now()

# Find the submissions which are duplicate in CodeChef retrieval
# These are introduced because of time format being something like 1 hour ago...
res = db.executesql(
"""
    SELECT id, user_id, custom_user_id, SUBSTRING_INDEX(view_link, '/', -1)
    FROM submission
    WHERE view_link != '' AND
          site='CodeChef' AND
          time_stamp BETWEEN '%s' AND '%s'
""" % (start_time, end_time))
print "Query complete", datetime.datetime.now()

duplicate_hash = {}

for row in res:
    dict_key = row[1:]
    if duplicate_hash.has_key(dict_key):
        duplicate_hash[dict_key].append(row[0])
    else:
        duplicate_hash[dict_key] = [row[0]]

print "Hash computation complete", datetime.datetime.now()
to_be_deleted = []
for key in duplicate_hash:
    if len(duplicate_hash[key]) > 1:
        print duplicate_hash[key]
        to_be_deleted.extend(duplicate_hash[key][1:])

print "To be deleted:", to_be_deleted
print "Starting delete query", datetime.datetime.now()
db(stable.id.belongs(to_be_deleted)).delete()
print "Delete complete", datetime.datetime.now()
