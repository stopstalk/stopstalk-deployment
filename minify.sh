#!/bin/bash
    : '
    Copyright (c) 2015-2018 Raj Patel(raj454raj@gmail.com), StopStalk

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
    '

all_js_files=("static/materialize/js/materialize.js"
    "static/js/bloodhound.js"
    "static/js/main.js"
    "static/js/jquery.js"
    "static/js/corejs-typeahead.bundle.js"
    "static/js/calendar.js"
    "static/js/web2py.js"
    "static/js/web2py-bootstrap3.js"
    #"static/js/appjs/google_analytics.js"
    "static/js/appjs/layout.js"
    "static/js/appjs/default/contests.min.js"
    "static/js/appjs/default/faq.js"
    "static/js/appjs/default/filters.js"
    "static/js/appjs/default/search.js"
    "static/js/appjs/default/friends.js"
    "static/js/appjs/default/leaderboard.js"
    "static/js/appjs/default/submissions.js"
    "static/js/appjs/default/todo.js"
    "static/js/appjs/testimonials/index.js"
    "static/js/appjs/problems/index.js"
    "static/js/appjs/problems/tag.js"
    "static/js/appjs/problems/trending.js"
    "static/js/appjs/problems/editorials.js"
    #"static/js/appjs/user/profile.js"
    "static/js/appjs/user/submissions.js"
    "static/js/materialize-tags.min.js")            

all_css_files=("static/materialize/css/materialize.css"
                "static/css/stopstalk.css"
                "static/css/style.css"
                "static/css/material.css"
                "static/css/materialize-tags.css"
                "static/css/reset.css"
                "static/css/web2py.css"
                "static/css/web2py-bootstrap3.css"
                "static/css/calendar.css"
                "static/css/owlie.css"
                "static/fa/css/font-awesome.css"
                "static/flag-icon/css/flag-icon.css")

if [ $# -lt 1 ]
then
    js_files=()
    css_files=()
else
    if [ "$1" = "ALL" ]
    then
        js_files=${all_js_files[*]}
        css_files=${all_css_files[*]}
    fi
fi

if [ ${#js_files[@]} != 0 ]
then
    for filename in $js_files;
    do
        echo "Minifying js file:" $filename
        newfilename=${filename%$".js"}
        uglifyjs $filename --output $newfilename.min.js
    done
fi

if [ ${#css_files[@]} != 0 ]
then
    for filename in $css_files;
    do
        echo "Minifying css file:" $filename
        newfilename=${filename%$".css"}
        uglifycss $filename --output $newfilename.min.css
    done
fi