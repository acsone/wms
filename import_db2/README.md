# Importing Alcyon DB2 datas

## Connection

### Port forwarding with the Raspberry
A raspberry has been installed at Alcyon as a proxy to DB2 database.

So you have to connect to this raspberry with port forwarding to the DB2 server.

 ```bash
 ssh pi@194.78.105.88 -L 8471:10.2.2.3:8471
 ```

Password and this command line are available in Lastpass in Alcyon shared fo

### ODBC Connection

Once port forwarding is enable, you can connect to Alcyon DB2 database via ODBC.

You have to install IBM DB2 drivers for ODBC to work. Drivers are available on IBM web site
The downloaded version is also available on fileserver:

`http://fileserver.camptocamp.com/2_global/4_it_ressources/software/databases/iseriesaccess_7.1.0-1.0_amd64.deb`

You need an odbc configuration file (path: ~/.odbc.ini) with Alcyon database configuration.

This file is available in Lastpass in Alcyon shared folder.

### Python client
In python, you can use the pyodbc lib:

 ```bash
 pip install --user pyodbc
 ```

And, in a Python shell:

 ```python
 In [1]: import pyodbc

 In [2]: conn = pyodbc.connect('DSN=Alcyon')

 In [3]: c = conn.cursor()

 In [4]: c.execute("select count(*) from sbdata.pgestion")
 Out[4]: <pyodbc.Cursor at 0x7ff3a1ea9f90>

 In [5]: c.fetchone()
 Out[5]: (29850, )

 In [6]: # 29 850 products in Alcyon databases
 ```

The 'Alcyon' value for DNS parameter is the section name in the odbc.ini configuration file.


## Play with the database

### Python shell

For searching data in better conditions, you can use the shell.py script which contains helping methods (feel free to add others)

Requirement:
```bash
pip install --user ipython
```

```bash
python import_db2/shell.py

In [1]: fetchall_dict("select clinum, clinom from gendata.client fetch first 5 rows only")
Out[1]:
[{'clinom': 'ALPHA REPARTITION             ', 'clinum': Decimal('1')},
 {'clinom': 'SAVENOR                       ', 'clinum': Decimal('2')},
 {'clinom': 'ASMA BORGERS                  ', 'clinum': Decimal('3')},
 {'clinom': 'DE VOOZORG S.M.               ', 'clinum': Decimal('4')},
 {'clinom': 'EPC 001 *                     ', 'clinum': Decimal('6')}]
```

### DB2 queries

* SQL limit: To limit a query you have to use `fetch first X rows only'

  ```sql
  select * from sbdata.pgestion fetch first 10 rows only;
  ```

 Don't try to replace FIRST by LAST, it doesn't work....

* Tables list, columns list: You can find these informations in qsys2.systables and qsys2.syscolumns

 ```sql
 select table_schema, table_name, column_name from qsys2.syscolumns
 where table_schema in ('SBDATA', 'GENDATA') and table_name in ('PGESTION', 'CLIENT')
 ```

### CSV Files generation

To generate import csv files for Odoo, use the importer.py script

 ```bash
 python import_db2/importer.py
 ```

This command will generate CSV files for the demo mode (subset of data, files are saved in odoo/data/demo/)


 ```bash
 python import_db2/importer.py --full
 ```

With --full flag, it will generate complete CSV files (files are saved in odoo/data/install/)

You can find in convertion.py (and mappings.py) how db2 entities are converted to Odoo entities.
