#!/usr/bin/python3
# -*- coding: utf-8 -*-
# based on this code
# http://code.activestate.com/recipes/577423-convert-csv-to-xml/

# convert Odoo csv files in xml files
# csv is easy to maintain but xml data have noupdate feature

import csv
import glob

MODULE = "alc_stock_storage_type"

NOUPDATE = 1
BOOLEAN = ("True", "False")
ERP_HEADER = """<?xml version="1.0"?>
<odoo noupdate="%s">"""

ERP_FOOTER = """</odoo>"""


def convert_relationnal_field2xml(tag, value):
    """Convert Relational fields"""
    mytag = tag
    for elm in ["/ids", "/id", ":id"]:
        mytag = mytag.replace(elm, "")
    if tag[-6:] == "ids/id":
        # 2many
        refs = []
        for xmlid in value.split(","):
            if "." not in xmlid:
                xmlid = "{}.{}".format(MODULE, xmlid)
            ref = "ref('{}')".format(xmlid)
            refs.append(ref)
        line = '{}" eval="[(6, 0, [{}])]" />\n'.format(mytag, ",".join(refs))
    else:
        # 2one
        line = '{}" ref="{}" />\n'.format(mytag, value)
    return line


def main():
    """Convert all csv files"""
    for csv_file in glob.glob("*.csv"):
        print(csv_file)  # pylint: disable=print-used
        csv_data = csv.reader(open(csv_file))
        sheet_name = csv_file.index(" - ")
        if sheet_name:
            csv_file = csv_file[sheet_name + 3 :]
        xml_file = csv_file.replace(".", "_").replace("_csv", ".xml")
        xml_data = open(xml_file, "w")
        xml_data.write(ERP_HEADER % NOUPDATE + "\n\n")
        row_num = 0
        for row in csv_data:
            if row_num == 0:
                tags = row
                for i, tag in enumerate(tags):
                    tags[i] = tag.replace(" ", "_")
            else:
                for i, tag in enumerate(tags):
                    char = False
                    # ambiguous column (char type but contains float string)
                    # should be mark by suffix |char
                    if tag[-5:] == "|char":
                        char = True
                    numeric = False
                    begin = '    <field name="'
                    try:
                        float(row[i])
                        numeric = True
                    except ValueError:  # pylint: disable=except-pass
                        pass
                    if tag == "id":
                        # 'id' column is supposed to be the first left
                        line = '  <record id="{}" model="{}">\n'.format(
                            row[i], csv_file[:-4]
                        )
                    elif "/" in tag or ":" in tag:
                        # relationnal fields
                        xml_suffix = convert_relationnal_field2xml(tag, row[i])
                        line = "{}{}".format(begin, xml_suffix)
                    elif char:
                        # numeric ghar field
                        line = '{}{}">{}</field>\n'.format(begin, tag[:-5], row[i])
                    elif numeric or row[i] in BOOLEAN:
                        line = '{}{}" eval="{}" />\n'.format(begin, tag, row[i])
                    else:
                        # basic fields
                        line = '{}{}">{}</field>\n'.format(begin, tag, row[i])
                    if row[i] or tag == "id":
                        xml_data.write(line)
                xml_data.write("  </record>" + "\n")
            row_num += 1
        xml_data.write(ERP_FOOTER)
        xml_data.close()


if __name__ == "__main__":
    main()
