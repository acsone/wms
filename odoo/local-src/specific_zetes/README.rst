.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==============
Specific Zetes
==============


This specific module offers tools to integrate a voice picking (Zetes) in Odoo:
- A controller to communicate with Zetes
- A error handler to catch all errors during communication
- An interface to easily expands existing tools
- Define on picking type if we need to print labels on a portable printer

Glossary
========

* Zetes: Zetes is the software to manage the communication between
the voice picker and Odoo
* Voice picker: The voice picker is a hardware.
It's composed of a small computer and a microphone
* REQU: It's an abbreviation for Request.
* RESP: It's an abbreviation for Response.
* RESU: It's an abbreviation for Result.
* Passport: The passport is a paper with all products picked.
It's allows to an another picker to check if all products picked
are really in the box. The "passport" is an option for special customers
who want have an order without any errors.
* Type of picking: Alcyon has 5 type of pick. A type of pick is a specific
zone in the Warehouse like "Aliment", "Médicament", ...


Features
========

This module manage all requests for following domain:
- Usercontext: Allows to retrieve some information about the picking
- Refdata: Allows to retrieve all type of picking (stock.picking.type)
- Assignement: Allows to search and assign a picking to a picking
- Itempick: Allows to retrieve all operations (stock.pack.operation)
- Location: Allows to retrieve all lots available
- Catchweight: Allows to write a picked quantity for an operation
- Print: Allows to print the passport or labels


Installation
============

There is no specific installation procedure for this module.

Configuration
=============

You need to configure the operator ID on each use to be able to use Zetes.

Credits
=======

Contributors
------------

* Sylvain Van Hoof <sylvain@okia.be>
