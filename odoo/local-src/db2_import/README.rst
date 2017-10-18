DB2 Importer
============

This module allows to import data from DB2 through the RasberryPI which act as a bridge.

This is a temporary module to do import of hot data (purchase, sales) from DB2 to odoo.

It copies all data in local replication of DB2 tables.
For each row of the table it creates queued job.

It implements imports for Sales orders and Purchase orders

3 importers will be implemented:

- Sales: to import sale order and sale order lines.
- Purchase: to import purchase order lines.
- 10 Customers: to import sale order only for 10 supplier.



Plus, two modes are available:

*History*

  Getting all objects and set them to done for the finished ones and let the other ones in draft.


*Final import*

  Getting all objects and creating intermediate states when necessary like back orders.


Running
-------

* Activate developer mode.
* Go in **Settings -> Technical -> DB2 -> DB2 Importer**
* Open an importer
* Configure the date range
* Click on Import



How it works
------------

When launching an import, first it will create a job per table and per object month called :code:`get_from_db2`.

:code:`get_from_db2` job will connect to DB2 and make a local table copy in postgres.

For each row inserted in the local copy for main objects, a job is created named :code:`create_or_update_record`

:code:`create_or_update_record` job will do the conversion and create the Odoo objects.



Dev setup
---------

To configure the connection, you need to set the following environment variables on you odoo service:

* :code:`DB2USER`
* :code:`DB2PWD`

Plus to be able to use the jobs you have to load the **queue_job** module by setting the :code:`--load`
odoo parameter.

Here is a minimal **docker-compose.override.yml** config::

    services:
      odoo:
        command: odoo --load="web,queue_job"
        tty: true
        stdin_open: true
        ports:
          - 8069
          - 8072
        volumes:
          - "data-odoo-pytest-cache:/opt/odoo/.cache"
          - "./odoo/src:/opt/odoo/src"
          - "./odoo/local-src:/opt/odoo/local-src"
          - "./odoo/external-src:/opt/odoo/external-src"
          - "./odoo/songs:/opt/odoo/songs"
          - "./odoo/migration.yml:/opt/odoo/migration.yml"
          - "./odoo/data:/opt/odoo/data"
        environment:
          RUNNING_ENV: dev
          # could be 'demo' for the minimal db or 'full' for the complete one
          MARABUNTA_MODE: demo
          # should not be set in production
          MARABUNTA_ALLOW_SERIE: 'True'
          DB2USER: camp2camp
          DB2PWD: is3ries4oo

To test it on a local instance, you need to start the container **pissh** which will take care
of the ssh connection with the RaspberryPI.

For this you need to add the private key in file **docker-compose.yml** to grant you access to the
RasberryPI

Example of docker-compose.override.yml::

  pissh:
    image: camptocamp/alcyon_pissh
    command: "ssh pi@194.78.105.88 -L 0.0.0.0:8471:10.2.3.99:8471 -N"
     environment:
       SSH_ID_RSA: |
         -----BEGIN RSA PRIVATE KEY-----
         # ...
         -----END RSA PRIVATE KEY-----


To launch it::

    docker-compose up -d pissh

(it might take few seconds to initiate the connection)

(if you want to launch pissh with :code:`docker-compose run` you will have to create links entry in **docker-compose.override.yml**)
