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
import json

# ----------------------------------------------------------------------------

def search():
    """
        @without query parameters returns the list of institutes and countries
        @with query parameters returns the list of registered users 
    """
    if len(request.vars) < 1:
        # Get all the list of institutes for the dropdown
        itable = db.institutes
        all_institutes = db(itable).select(itable.name,
                                           orderby=itable.name)
        all_institutes = [x.name.strip("\"") for x in all_institutes]
        all_institutes.append("Other")

        country_name_list = current.all_countries.keys()
        country_name_list.sort()

        return response.json(dict(all_institutes=all_institutes,
                    country_name_list=country_name_list))

    atable = db.auth_user
    ftable = db.following
    q = request.get_vars.get("q", None)
    institute = request.get_vars.get("institute", None)
    country = request.get_vars.get("country", None)

    # Build query for searching by first_name, last_name & stopstalk_handle
    query = ((atable.first_name.contains(q)) | \
             (atable.last_name.contains(q)) | \
             (atable.stopstalk_handle.contains(q)))

    if utilities.is_stopstalk_admin(session.user_id):
        query |= (atable.email.contains(q))

    # Search by profile site handle
    for site in current.SITES:
        field_name = site.lower() + "_handle"
        query |= (atable[field_name].contains(q))

    if auth.is_logged_in():
        # Don't show the logged in user in the search
        query &= (atable.id != session.user_id)

    # Search by institute (if provided)
    if institute:
        query &= (atable.institute == institute)

    # Search by country (if provided)
    if country:
        query &= (atable.country == country)

    query &= (atable.registration_key == "")

    # Columns of auth_user to be retrieved
    columns = [atable.id,
               atable.first_name,
               atable.last_name,
               atable.stopstalk_handle]

    for site in current.SITES:
        columns.append(atable[site.lower() + "_handle"])

    rows = db(query).select(*columns,
                            orderby=[atable.first_name, atable.last_name])

    return response.json(dict(users=rows))

# ----------------------------------------------------------------------------
