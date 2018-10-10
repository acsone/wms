## Specific tasks

### data.make-csv-diff

This task compare 2 csv files and create multiple csv files
to be loaded in the next version.

Those files are used to 


Parameters:

* filename: name of file inside directory "odoo/data/install"


Process:

Provided file will be compared to the same file path appending ".former"
at the end of it. ".former" files are generated after an importer from DB2. (See DB2 import)

It will generate csv files in a folder in "odoo/data/update/10.x+1.0" (FIXME it should be 10.x.y+1)

Those diff files will contain only actual changes.

For each created file, an entry is added in odoo/migration.yml


Example:

```
$ cat odoo/VERSION
10.20.3
$ invoke data.make-csv-diff --filename=product.csv
```

Will create csv files in: odoo/data/update/10.21.0
and you will find this in your odoo/migration

```
      modes:
        full:
          operations:
            post:
              - bin/importer.sh songs.install.data_full::import_products /odoo/data/update/10.21.0/product.new.csv
              - bin/importer.sh songs.install.data_full::import_products /odoo/data/update/10.21.0/product.change-width-length-depth.csv
              - bin/importer.sh songs.install.data_full::import_products /odoo/data/update/10.21.0/product.change-width-length-taxes_id-depth.csv
              - bin/importer.sh songs.install.data_full::import_products /odoo/data/update/10.21.0/product.change-web_published-name-depth-width-length-state_id-active.csv
              - bin/importer.sh songs.install.data_full::import_products /odoo/data/update/10.21.0/product.change-width-length-depth-orderpoint_min-orderpoint_max.csv
              ...
```


WARNING:

1. Check former files

Be sure to generate diff on the right former files to have a coherent diff file.
If needed you can use:

```
cd odoo/data/install
cp product.csv product.csv.new
git checkout 10.20.0 product.csv
cp product.csv product.csv.former
cp product.csv.new product.csv
```

2. Tests

Those data are not tested with travis

It is important to test them on top of last integration locally.

A dump needs to be asked to jean.cardona@limelogic.be and eric.granados@limelogic.be
It should land on pp-erp.alcyonbelux.be:/var/backups


3. Updates on partners needs to deactivate the VIES check

Some partners have a wrong a non valid VAT number, we don't want to check it on import.
Thus here is how to disable it:

```
  - anthem songs.upgrade.common::deactivate_check_on_vat
  - bin/importer.sh songs.install.data_full::import_clients_addresses /odoo/data/install/customer_address.csv
  - anthem songs.install.accounting::activate_check_on_vat
```

