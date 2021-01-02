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

# Atleast 3 users of an institute must have entered the
sql_query = """
SELECT institute, country
FROM auth_user
WHERE institute != "Other" and country != ""
GROUP BY institute, country
HAVING count(*) > 2;
"""
institute_to_country = dict(db.executesql(sql_query))
for institute in institute_to_country:
    print institute, "->", institute_to_country[institute]

atable = db.auth_user
cftable = db.custom_friend

updated_count = 0
for record in db(atable.institute.belongs(institute_to_country.keys())).select():
    if not record.country:
        record.update_record(country=institute_to_country[record.institute])
        updated_count += 1

for record in db(cftable.institute.belongs(institute_to_country.keys())).select():
    if not record.country:
        record.update_record(country=institute_to_country[record.institute])
        updated_count += 1

print "Total updated:", updated_count
