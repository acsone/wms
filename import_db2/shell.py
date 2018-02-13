# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from IPython.terminal.embed import InteractiveShellEmbed
import pyodbc
import csv
import sys

cursor = None

def create_csv_file(rows, filename):
    print "Start generating csvfile"
    with open(filename, 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([i[0] for i in cursor.description])  # headers
        i = 0
        nb = len(rows)
        for r in rows:
            i += 1
            progress = float(i) / nb
            print "\r[ {0:40s} ] {1:.1f}%".format(
                '#' * int(progress * 40),
                progress * 100),
            sys.stdout.flush()
            writer.writerow(r)
        print  # add newline
    return "%s rows saved in %s" % (nb, filename)


def fetchall_dict(query, copy_to=None):
    """ Execute the *query* on db2 database and transform the results in
    a list of dict [{'column_name': value, ...}]

    copy_to: allows to export in a csv file.
    """
    global cursor
    cursor.execute(query)
    rows = cursor.fetchall()
    if rows:
        if copy_to:
            return create_csv_file(rows, copy_to)
        rows = [
            {col.lower(): row[idx] for idx, col in enumerate(
                [d[0] for d in row.cursor_description]
            )} for row in rows
        ]

    return rows


def shell():
    """ Open an ipython shell with connected connection to DB2 database.
    """
    connection = pyodbc.connect("DSN=Alcyon")
    try:
        global cursor
        cursor = connection.cursor()
        shell = InteractiveShellEmbed()
        shell.mainloop()
    finally:
        connection.close()


if __name__ == "__main__":
    shell()
