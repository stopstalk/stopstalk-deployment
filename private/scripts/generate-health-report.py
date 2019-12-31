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

import utilities
from gluon import current

metric_handlers = utilities.init_metric_handlers(log_to_redis=True)

html_body = "<html><head><title>StopStalk submission retrieval</title></head><body><h2>StopStalk Submission Retrieval Report</h2>"
for site in current.SITES:
    lower_site = site.lower()
    html_body += "<h3><u>%s</u></h3>" % site
    html_body += "<table border='1' cellpadding='4' cellspacing='0'>"
    for key in metric_handlers[lower_site]:
        html_body += metric_handlers[lower_site][key].get_html()
        metric_handlers[lower_site][key].flush_keys()
    html_body += "</table><br/>"
    html_body += "________________________________________________<br/>"

html_body += "<h3><u>Overall</u></h3>"
html_body += "<table border='1' cellpadding='4' cellspacing='0'>"
for key in metric_handlers["overall"]:
    html_body += metric_handlers["overall"][key].get_html()
    metric_handlers["overall"][key].flush_keys()

html_body += "</table><br/>"
html_body += "________________________________________________<br/>"

html_body += "</body></html>"

current.send_mail(to="contactstopstalk@gmail.com",
                  subject="StopStalk Submission Retrieval Report",
                  message=html_body,
                  mail_type="admin",
                  bulk=False)
