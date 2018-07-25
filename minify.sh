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

readarray all_js_css_files < static_files_list.txt

if [ $# -lt 1 ]
then
    static_files=()
else
    if [ "$1" = "ALL" ]
    then
        static_files=${all_js_css_files[*]}
    fi
fi

if [ ${#static_files[@]} != 0 ]
then
    for filename in $static_files;
    do
        newfilename=static/minified_files/${filename}
        filename=static/${filename}
        if [ "${filename: -3}" = ".js" ]
        then
            js_file=${newfilename%$".js"}.min.js
            echo "Minifying js file:" $filename
            uglifyjs $filename --mangle --output $js_file
        else
            css_file=${newfilename%$".css"}.min.css
            echo "Minifying css file:" $filename
            uglifycss $filename --output $css_file
        fi
    done

fi