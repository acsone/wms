# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from IPython.terminal.embed import InteractiveShellEmbed
import pyodbc
import csv
import sys

cursor = None

def write_csv_file(csvfile, rows, add_headers=True):
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
        # automatically trim each field
        r = [col.strip() if isinstance(col, str) else col for col in r]
        writer.writerow(r)
    print  # add newline


def create_csv_file(rows, filename):
    print "Creating a csvfile"
    with open(filename, 'w') as csvfile:
        write_csv_file(csvfile, rows)
    nb = len(rows)
    return "%s rows saved in %s" % (nb, filename)


def chunk_query(query, copy_to, chunk_size):
    nb = 0
    i = 1
    with open(copy_to, 'w') as csvfile:
        cursor.execute(query)
        while True:
            rows = cursor.fetchmany(chunk_size)
            if not rows:
                break
            print "Chunk %s: from %s to %s" % (i, nb + 1, nb + len(rows))
            nb = nb + len(rows)
            write_csv_file(csvfile, rows, add_headers=(i == 1))
            i = i + 1
    return "%s rows saved in %s" % (nb, copy_to)


def fetchall_dict(query, copy_to=None, chunk_size=None):
    """ Execute the *query* on db2 database and transform the results in
    a list of dict [{'column_name': value, ...}]

    copy_to: file path, if provided export result of query in a csv file.
    chunk_size: for big queries split the fetch by chunk to save memory space
    """
    global cursor
    if chunk_size:
        if not copy_to:
            return "chunk query is only avalaible with copy to csv"
        return chunk_query(query, copy_to, chunk_size)
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
