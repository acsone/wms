This module allows to import data from DB2

This is a temporary module to do import of hot data from DB2 to odoo

It copies all data in local replication of DB2 tables
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
