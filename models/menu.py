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

response.logo = A(B("StopStalk"), _class="navbar-brand",
                  _href=URL('default', 'index'),
                  _id="web2py-logo")
response.title = request.application.replace('_',' ').title()
response.subtitle = ''

response.meta.author = 'StopStalk admin@stopstalk.com'
response.meta.keywords = 'stopstalk, raj454raj, competitive programming, algorithms, algorithmic progress'
response.meta.generator = ''

response.google_analytics_id = None

response.menu = []

def get_menu_tuple(icon_class, tooltip, button_label, url, new_item=False):
    item_tuple = [I(_class="fa fa-2x " + icon_class),
                  tooltip,
                  button_label,
                  url,
                  ""]
    if new_item:
        item_tuple[4] = SPAN(_class="new badge pulse")
    return item_tuple

if session.user_id:
    response.menu += [get_menu_tuple("fa-user-secret",
                                     T("Custom Friend"),
                                     "Nav Custom Friend",
                                     URL("user", "custom_friend")),
                      get_menu_tuple("fa-user-plus",
                                     T("Your Friends"),
                                     "Nav Friends",
                                     URL("default", "friends")),
                      get_menu_tuple("fa-list-alt",
                                     T("Todo List"),
                                     "Nav Todo",
                                     URL("default", "todo"))]

response.menu += [get_menu_tuple("fa-users",
                                 T("User Editorials"),
                                 "Nav User editorials",
                                 URL("default", "user_editorials")),
                  get_menu_tuple("fa-search",
                                 T("Search Friends"),
                                 "Nav Search",
                                 URL("default", "search")),
                  get_menu_tuple("fa-calendar-check-o",
                                 T("Upcoming Contests"),
                                 "Nav Contests",
                                 URL("default", "contests")),
                  get_menu_tuple("fa-tag",
                                 T("Search Problems"),
                                 "Nav Problem Search",
                                 URL("problems", "search")),
                  get_menu_tuple("fa-bar-chart",
                                 T("Leaderboard"),
                                 "Nav Leaderboard",
                                 URL("default", "leaderboard")),
                  get_menu_tuple("fa-line-chart",
                                 T("Trending Problems"),
                                 "Nav Trending Problems",
                                 URL("problems", "trending")),
                  get_menu_tuple("fa-filter",
                                 T("Submission Filters"),
                                 "Nav Filters",
                                 URL("default", "filters")),
                  get_menu_tuple("fa-heart",
                                 T("Testimonials"),
                                 "Nav Testimonials",
                                 URL("testimonials", "index")),
                  get_menu_tuple("fa-bullhorn",
                                 T("Feature Updates"),
                                 "Nav Feature Updates",
                                 URL("default", "updates"))]

if "auth" in locals(): auth.wikimenu()

# =============================================================================
