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

# This script is used to rename files on s3 bucket from <user_id>.pdf to zero padded
# with the user id
# Example:
# ========
# 1.pdf becomes 000000001.pdf
# This file needs to be executed in the same directory where
# aws s3 sync s3://stopstalk-files/resumes . is called

import os
import re

S3_BUCKET = "stopstalk-files"
all_files = []
for _, _, files in os.walk("."):
    all_files = files

for one_file in all_files:
    if re.match("^\d+\.pdf$", one_file) is None or \
       len(one_file) == 9 + 4: # 9 digit user_id, 4 for .pdf
        print "Skipping", one_file
        continue
    user_id = one_file.replace(".pdf", "")
    command = "aws s3 mv s3://%s/resumes/%s s3://%s/resumes/%s" % (S3_BUCKET, one_file, S3_BUCKET, "%.9d.pdf" % int(user_id))
    os.system(command)
