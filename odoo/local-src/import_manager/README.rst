.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==============
Import Manager
==============

Import Manager module is a generic module to manage any imports.
Format supported:
   - CSV

This module will load your file in DB and execute a specific method.

Configuration
============

After installation, you need to configure the module.
Go to "Configuration" => "Technique" (debug mode required) => "Imports" => "Configuration"
- Import IN path: The path where the files are located
- Import OUT path: The path where the module will move files after import
- Import FAILURE path: The path where the module will move files in case of errors

Create an import
================

1.
To create an import you need to create a new model.
This module HAVE TO inherit the model 'import.model'.

2.
Add the dict columns_mapping.
This dict will link file column with odoo field
Eg:
columns_mapping = {
   'my_first_csv_column': 'name',
   'my_second_csv_column': 'partner_name',
}

3.
Create Odoo fields (according the columns mapping)
Tips: create only char fields. It's more safe
Eg:
name = fields.Char()
partner_name = fields.Char()

4.
Inherit the method execute_import
@api.multi
def execute_import(self, logger_id):
   ------
   do a lot of thing
   ------

   return True

WARNING: If the method doesn't return True, the import will be flag in "error"

5.
Create a new import.file

Credits
=======

Contributors
------------

* Sylvain Van Hoof <sylvain@okia.be>
