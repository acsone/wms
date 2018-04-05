## csv files from DB2

# Requirements

Install git-lfs: https://github.com/git-lfs/git-lfs/wiki/Installation

# Connect to db2

    ssh pi@194.78.105.88 -L 0.0.0.0:8471:10.2.2.3:8471 -i ~/.ssh/ssh_alcyon_rsa -o ServerAliveInterval=30

# Launch shell to connect to DB2 through pyodbc

    python import_db2/shell.py

# Generate files

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
