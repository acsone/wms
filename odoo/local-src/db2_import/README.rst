DB2 Importer
============

This module allows to import data from DB2 through the RasberryPI which act as a bridge.

This is a temporary module to do import of hot data (purchase, sales) from DB2 to odoo

It copies all data in local replication of DB2 tables.
For each row of the table it creates queued job.

It implements imports for Sales orders and Purchase orders

3 importers will be implemented:

- Sales: to import sale order and sale order lines.
- Purchase: to import purchase order lines.
- 10 Customers: to import sale order only for 10 supplier.



Plus, two modes are available:

History
Getting all objects and set them to done for the finished ones and let the other ones in draft.


Final import
Getting all objects and creating intermediate states when necessary like back orders.


Running
-------

* Activate developer mode.
* Go in Settings -> Technical -> DB2 -> DB2 Importer
* Open an importer
* Configure the date range
* Click on Import



How it works
------------

When launching an import, first it will create a job per table and per object month called `get_from_db2`.

`get_from_db2` job will connect to DB2 and make a local table copy in postgres.

For each row inserted in the local copy for main objects, a job is created named `create_or_update_record`

`create_or_update_record` job will do the conversion and create the Odoo objects.



Dev setup
---------

To test it on a local instance, you need to start the container `pissh` which will take care
of the ssh connection with the RaspberryPI.

For this you need to add the private key in file `docker-compose.yml` to grant you access to the
RasberryPI

To launch it:

`docker-compose up -d pissh`

(it might take few seconds to initiate the connection)
(if you want to launch pissh with `docker-compose run` you will have to create links entry in `docker-compose.override.yml`This module allows to import data from DB2)
