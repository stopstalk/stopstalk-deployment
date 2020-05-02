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
from gluon import current, IMG, DIV, TABLE, THEAD, HR, H5, \
                  TBODY, TR, TH, TD, A, SPAN, INPUT, I, P, \
                  TEXTAREA, SELECT, OPTION, URL, BUTTON, TAG

class BaseCard:
    def __init__(self, user_id, card_type):
        self.user_id = user_id
        self.card_type = card_type

    def get_html(self, **args):
        return DIV(DIV(DIV(SPAN(args["card_title"], _class="card-title"),
                           P(args["card_text"]),
                            _class="card-content white-text"),
                       DIV(A(args["card_action_text"],
                             _href=args["card_action_url"]),
                           _class="card-action"),
                       _class="card blue-grey darken-1"),
                   _class="col s4")

    def get_data(self):
        pass

class StreakCard(BaseCard):
    def __init__(self, user_id):
        self.genre = StreakCard.__name__
        self.user_id = user_id
        self.card_title = "Keep your Streak going!"
        BaseCard.__init__(self, user_id, "simple_with_cta")

    def get_html(self):
        card_html = BaseCard.get_html(self, **dict(
                       card_title=self.card_title,
                       card_text="This is some long text in each card",
                       card_action_text="Action CTA",
                       card_action_url="#"
                    ))
        return card_html

    def get_data(self):
        pass

    def should_show(self):
        pass


