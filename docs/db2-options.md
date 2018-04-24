# DB2 options

The module `importer_db2` requires access to DB2 server to pull the data.

Here are the environment variables to set:

```
DB2USER: db2 role
DB2PWD: db2 password
DB2HOST: ip of db2 server or 'pissh'
```

If intramuros, you can use DB2HOST with the ip address of the server

PROD: 10.2.2.3
REPLICATE: 10.2.3.99

Otherwise from camptocamp platform you need to activate the pissh container with SSH key.
And set `DB2HOST=pissh`

# DB2 modes

When deploying a release from an empty database, the migration steps will setup automatically
the importer from DB2. Here are the available setup for those.


```
DB2IMPORT_MODE: mode of import, possible values are 'history' or 'final_update'
DB2IMPORT_YEARS: to change the number of years in the past we import
DB2IMPORT_MONTHS: to change the number of months in the past we import (it adds up to the years)

```

The go-live will require 2 releases:
- one release with 'history' mode
- a second release with the 'final_update' mode

This because the time of importing history with the last changes in data takes some times.

# DB2 modes Integration env only

A subset of 10 client was selected to do extended importation of integration.
Here you can disable it or modify it.


```
DB2IMPORT_10CLI: put 'False' to disable it
DB2IMPORT_10CLI_YEARS: to change the number of years in the past we import for the 10 clients only
DB2IMPORT_10CLI_MONTHS: to change the number of months in the past we import for the 10 clients only (it adds up to the years)
```

If the range is lower than the main import, the 10 client extension will be ignored.

For instance if you set `DB2IMPORT_YEARS = 2` and `DB2IMPORT_10CLI_YEARS = 1`,
nothing needs to be done for the 10 selected clients as all the wanted
data is already imported.
