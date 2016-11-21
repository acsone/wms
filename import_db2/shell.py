# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from IPython.terminal.embed import InteractiveShellEmbed
import pyodbc

cursor = None


def fetchall_dict(query):
    """ Execute the *query* on db2 database and transform the results in
    a list of dict [{'column_name': value, ...}]
    """
    global cursor
    cursor.execute(query)
    rows = cursor.fetchall()
    if rows:
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
