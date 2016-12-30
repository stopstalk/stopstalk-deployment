# -*- coding: utf-8 -*-
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

response.logo = A(B("StopStalk"), _class="navbar-brand",
                  _href=URL('default', 'index'),
                  _id="web2py-logo")
response.title = request.application.replace('_',' ').title()
response.subtitle = ''

response.meta.author = 'StopStalk admin@stopstalk.com'
response.meta.description = 'Retrieves submissions of friends\' from various competitive websites and analyse them'
response.meta.keywords = 'stopstalk, raj454raj, competitive programming, algorithms, algorithmic progress'
response.meta.generator = ''

response.google_analytics_id = None

response.menu = []

def get_tooltip_data(tooltip):
    return dict(position="bottom", delay="40", tooltip=tooltip)

def get_menu_tuple(icon_class, tooltip, url):
    return (I(_class="fa fa-2x tooltipped " + icon_class,
              data=get_tooltip_data(tooltip)),
            False,
            url,
            [])

if session.user_id:
    response.menu += [get_menu_tuple("fa-bell-o",
                                     T("Notifications"),
                                     URL("default", "notifications")),
                      get_menu_tuple("fa-user-secret",
                                     T("Custom Friend"),
                                     URL("user", "custom_friend")),
                      get_menu_tuple("fa-users",
                                     T("Your Friends"),
                                     URL("default", "friends"))]

response.menu += [get_menu_tuple("fa-search",
                                 T("Search Friends"),
                                 URL("default", "search")),
                  get_menu_tuple("fa-calendar-check-o",
                                 T("Upcoming Contests"),
                                 URL("default", "contests")),
                  get_menu_tuple("fa-bar-chart",
                                 T("Leaderboard"),
                                 URL("default", "leaderboard")),
                  get_menu_tuple("fa-line-chart",
                                 T("Trending Problems"),
                                 URL("problems", "trending")),
                  get_menu_tuple("fa-filter",
                                 T("Submission Filters"),
                                 URL("default", "filters")),
                  get_menu_tuple("fa-tag",
                                 T("Search by tags"),
                                 URL("problems", "tag"))]

if "auth" in locals(): auth.wikimenu()

# =============================================================================
