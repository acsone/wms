# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

""" Split a csv file in multiple sub files but groups by key

Split is done by dividing the number of row per -s
or split by a defined number of rows
It will keep writing in the same file going above the size limit till
all next row with same key are written.

We assume csv file is ordered by the grouping key column.

Usage:
csv-split.py -f odoo/data/sale_order_line.csv -d /tmp -s 4 -k 'order_id/id'
csv-split.py -f odoo/data/sale_order_line.csv -d /tmp -s 4 -k 'order_id/id'

"""

import os
import csv

from optparse import OptionParser

parser = OptionParser()
parser.add_option('-f', dest="filename", help="Filename of the csv file")
parser.add_option('-d', dest="dest_dir",
                  help="Dirname in which to write the csv files")
parser.add_option('-s', dest="nb_split", default=0,
                  help="Number of split to create")
parser.add_option('-n', dest="file_size", default=0,
                  help="Number of line per file")
parser.add_option('-k', dest="key_group", default=None,
                  help="Key for which entries will be kept in same file")

(options, args) = parser.parse_args()
csv_path = options.filename
dest_dir = options.dest_dir
nb_split = int(options.nb_split)
file_size = int(options.file_size)
key_group = options.key_group

# -s and -n are exclusives
if not file_size and not nb_split:
    print("You need to provide one of those options: -s or -n ")
    exit()

if file_size and nb_split:
    print("Only one of those options must be used: -s or -n.")
    exit()

nb_rows = 0
with open(csv_path) as csv_file:
    reader = csv.DictReader(csv_file)
    for row in reader:
        nb_rows += 1
if not file_size:
    file_size = nb_rows / nb_split
else:
    # ceil division to have minimum 1 split
    nb_split = (nb_rows / file_size) + 1


with open(csv_path) as csv_file:
    reader = csv.DictReader(csv_file)
    fieldnames = reader.fieldnames

    rejected_row = None
    for split_no in range(nb_split):

        line_counter = 0
        last_key = None
        current_row = None
        split_path = os.path.join(dest_dir, "%02i" % split_no)
        with open(split_path, 'wb') as split_file:
            writer = csv.DictWriter(split_file, fieldnames=fieldnames)
            writer.writeheader()

            # write row rejected from previous file
            # in the newly opened file
            if rejected_row:
                writer.writerow(rejected_row)
                rejected_row = None
                line_counter += 1

            current_key = None
            while True:
                try:
                    current_row = reader.next()
                except StopIteration:
                    break
                if key_group:
                    current_key = current_row[key_group]
                # stop writing in the current file if we have reached
                # size limit unless there is a group to continue
                # or we are writing the last file
                if (line_counter >= file_size and
                        split_no != nb_split - 1 and
                        (current_key != last_key or not key_group)):
                    rejected_row = current_row
                    break
                writer.writerow(current_row)
                line_counter += 1
                last_key = current_key
