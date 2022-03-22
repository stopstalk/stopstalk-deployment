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
import csv
import os
import time
import xlsxwriter

from prettytable import PrettyTable
from prettytable import PLAIN_COLUMNS

atable = db.auth_user

users = db(atable.institute == "Lovely Professional University").select(limitby=(0, 100))

stats_table = PrettyTable()

field_names = ["StopStalk handle", "Total solved", "Total problems", "StopStalk Rating"]

for site in current.SITES:
    field_names.append(site + " Accuracy")
    field_names.append(site + " Solved")

field_names.append("Maximum day streak")

stats_table.field_names = field_names
rows = [field_names]

for user in users:
    result = utilities.get_rating_information(user.id,
                                     False,
                                     False)
    print "Added result for user:", user.stopstalk_handle
    row = [user.stopstalk_handle, result["solved_problems_count"], result["total_problems_count"], user.stopstalk_rating]
    for site in current.SITES:
        if site in result["site_accuracies"]:
            row.append(result["site_accuracies"][site])
        else:
            row.append("-")
        if site in result["solved_counts"]:
            row.append(result["solved_counts"][site])
        else:
            row.append(0)
    row.append(result["max_day_streak"])
    rows.append(row)
    # time.sleep(0.1)
    # stats_table.add_row(row)

# Create a workbook and add a worksheet.
workbook = xlsxwriter.Workbook('report.xlsx')
worksheet = workbook.add_worksheet()
worksheet.set_column(0, len(field_names), 15)

with open('report.csv', 'w') as file:
    writer = csv.writer(file)
    writer.writerows(rows)

cell_format = workbook.add_format()
cell_format.set_center_across()

header_cell_format = workbook.add_format()
header_cell_format.set_center_across()
header_cell_format.set_bold()
header_cell_format.set_border(1)
header_cell_format.set_bg_color("#b1e3f2")
header_cell_format.set_border_color("#a7a9ab")
header_cell_format.set_text_wrap()

with open('report.csv', 'rt') as excel_file:
    reader = csv.reader(excel_file)
    for r, row in enumerate(reader):
        for c, col in enumerate(row):
            if r == 0:
                worksheet.write(r, c, col, header_cell_format)
            else:
                worksheet.write(r, c, col, cell_format)
workbook.close()

os.remove("report.csv")

# stats_table.set_style(PLAIN_COLUMNS)
# stats_table.padding_width = 2
# stats_table.align = "c"

# print stats_table.get_string()