"""
    Copyright (c) 2015 Raj Patel(raj454raj@gmail.com), StopStalk

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

from gluon import *

def navbar(auth_navbar):
    """
        Custom navbar dropdown
    """

    bar = auth_navbar
    user = bar["user"]

    if not user:
        toggletext = ("Login")
        toggle = A(B(I(_class="fa fa-sign-in"), " ",
                       toggletext),
                   _href="",
                   _class="dropdown-toggle",
                   _rel="nofollow",
                   **{"_data-toggle": "dropdown"})

        dropdown = UL(LI(A(I(_class="fa fa-sign-in"), " ",
                           current.T("Login"),
                           _href=bar["login"],
                           _rel="nofollow")),
                      LI('', _class="divider"),
                      LI(A(I(_class="fa fa-user-plus"), " ",
                           current.T("Sign Up"),
                           _href=bar["register"],
                           _rel="nofollow")),
                      _class="dropdown-menu", _role="menu",
                      )

    else:
        toggletext = B(STRONG("%s %s" % (bar["prefix"], user)))
        toggle = A(toggletext,
                   _href="",
                   _class="dropdown-toggle",
                   _rel="nofollow",
                   **{"_data-toggle": "dropdown"})

        li_custom = LI(A(I(_class="fa fa-user"), ' ',
                         current.T("My Profile"),
                         _href=URL("user", "profile"),
                         rel="nofollow"))
        dropdown = UL(li_custom, _class="dropdown-menu", _role="menu")

        li_custom = LI(A(I(_class="fa fa-list"), ' ',
                         current.T("My Submissions"),
                         _href=URL("user", "submissions", vars={'page': 1}),
                         rel="nofollow"))
        dropdown.append(li_custom)

        li_profile = LI(A(I(_class="fa fa-pencil-square-o"), ' ',
                          current.T("Update details"),
                          _href=bar["profile"], _rel="nofollow"))
        dropdown.append(li_profile)

        li_passwd = LI(A(I(_class="fa fa-lock"), ' ',
                           current.T("Change Password"),
                           _href=bar["change_password"], _rel="nofollow"))
        dropdown.append(li_passwd)

        dropdown.append(LI('', _class="divider"))

        li_logout = LI(A(I(_class="fa fa-sign-out"), ' ',
                         current.T("Logout"),
                         _href=bar["logout"], _rel="nofollow"))
        dropdown.append(li_logout)

    return LI(toggle, dropdown, _class="dropdown")
