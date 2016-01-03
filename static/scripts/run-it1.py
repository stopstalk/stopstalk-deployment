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

import os
from datetime import datetime

stopstalk_logs = "/root/stopstalk-logs/"
if not os.path.exists(stopstalk_logs):
    print "Creating directory " + stopstalk_logs + " ..."
    os.makedirs(stopstalk_logs)

os.chdir(stopstalk_logs)
today = str(datetime.now()).split(" ")[0]
today_dir = stopstalk_logs + today + "/"
if not os.path.exists(today_dir):
    print "Creating directory " + today + " ..."
    os.makedirs(today_dir)

os.chdir(today_dir)

directory = "/home/www-data/web2py/"

print "Retrieving submissions ..."
os.system("python " + directory + \
          "web2py.py -S stopstalk -M -R " + directory + \
          "applications/stopstalk/static/scripts/submissions1.py > " + \
          today_dir + "submissions1.log")
os.system("cat " + today_dir + "submissions1.log")
