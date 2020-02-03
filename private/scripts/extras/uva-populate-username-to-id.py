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

import urllib3
from sites.init import *

urllib3.disable_warnings()

u2idtable = uvadb.usernametoid
atable = db.auth_user
cftable = db.custom_friend

current_handles = uvadb(u2idtable).select(u2idtable.username)
current_handles = set([x.username for x in current_handles])

all_uva_handles = set([])

handles = db(atable.uva_handle != "").select(atable.uva_handle)
all_uva_handles = all_uva_handles.union(set([x.uva_handle for x in handles]))

handles = db(cftable.uva_handle != "").select(cftable.uva_handle)
all_uva_handles = all_uva_handles.union(set([x.uva_handle for x in handles]))

import requests

for handle in (all_uva_handles - current_handles):
    response = get_request("http://uhunt.felix-halim.net/api/uname2uid/" + handle)
    if response.status_code == 200 and response.text.strip() != "0":
        print handle, response.text, "added"
        u2idtable.insert(username=handle,
                         uva_id=response.text)
