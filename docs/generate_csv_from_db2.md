# csv files from DB2

## Requirements

Install git-lfs: https://github.com/git-lfs/git-lfs/wiki/Installation

## Connect to db2

    ssh pi@194.78.105.88 -L 0.0.0.0:8471:10.2.2.3:8471 -i ~/.ssh/ssh_alcyon_rsa -o ServerAliveInterval=30

# Cold data (product, partners, ...)

Most data don't move much, but there are always few changes between 2 releases. Thus we need to update the data.
For each data release you will need to update them.

Generate files:

    python import_db2/importer.py --full

For more details see [Importing Alcyon DB2 data](../import_db2/README.md)

# Cold data (product, partners, ...) - Diff

Sometimes you don't want to reload all the data for a single change.
In such case you might prefer to load only the actual changes.

You can use the following invoke task for this:

[invoke data.make-csv-diff](./invoke.local.md)


# Transactional data (sale orders, purchase orders)

This action is rarely required. Last generation was done until end of March 2018.
A couple of months is not much compared to 2 years. To refresh eventually on last data import from scratch.

For those data as the volume of data to pull from DB2 history is massive we do a local copy of the DB2 tables.
To do so we compile some csv files which will be later used by jobs to convert objects 1 by 1.

Then the importer will catch up with the remaining data to import.

Launch shell to connect to DB2 through pyodbc:

    python import_db2/shell.py

Generate files:

Here we take all rows from 2016-01-01 to 2018-03-31


    # sales
    fetchall_dict("SELECT * FROM SBDATA.pentcdcl WHERE ecccss = 20 AND (ecccaa = 16 OR ecccaa = 17 OR (ecccaa = 18 AND ecccmm <= 3))", copy_to='/tmp/pentcdcl_2016-01_2018-03.csv', chunk_size=100000);
    fetchall_dict("SELECT * FROM SBDATA.pdetcdcl WHERE dcccss = 20 AND (dcccaa = 16 OR dcccaa = 17 OR (dcccaa = 18 AND dcccmm <= 3))", copy_to='/tmp/pdetcdcl_2016-01_2018-03.csv', chunk_size=100000);

    # purchases
    fetchall_dict("SELECT * FROM SBDATA.pentcdfo WHERE ecfcss = 20 AND (ecfcaa = 16 OR ecfcaa = 17 OR (ecfcaa = 18 AND ecfcmm <= 3))", copy_to='/tmp/pentcdfo_2016-01_2018-03.csv', chunk_size=100000);
    fetchall_dict("SELECT * FROM SBDATA.pdetcdfo WHERE dcfcss = 20 AND (dcfcaa = 16 OR dcfcaa = 17 OR (dcfcaa = 18 AND dcfcmm <= 3))", copy_to='/tmp/pdetcdfo_2016-01_2018-03.csv', chunk_size=100000);

    # moves
    fetchall_dict("SELECT * FROM SBDATA.mvtlot WHERE mltcss = 20 AND (mltdaa = 16 OR mltdaa = 17 OR (mltdaa = 18 AND mltcmm <= 3))", copy_to='/tmp/mvtlot_2016-01_2018-03.csv', chunk_size=100000);


Then move the files in odoo/data/install/db2
Make sure you use those files in `copy_from*.sql` files.

As those files are big we manage them with git lfs.
All csv files located in odoo/data/install/db2 will be stored on lfs.
