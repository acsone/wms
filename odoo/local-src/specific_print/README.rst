.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===========
Stock Print
===========

Print stock labels and package labels.
* Add a wizard to easily print product labels and package labels.
  You will be able to choose a printer by his printer number
* Contains label codes for lot, pack and product
   - Lot label: Code ZEBRA (ZPL) - code without template
   - Pack label: Code ZEBRA (ZPL) - code with template to load (please read installation)
   - Product label: Code Toshiba (TPCL) - code without templates

Installation
============

There is no specific installation procedure for this module.

Configuration
=============

You have to install the template for pack label in each printer.
This process is completely outside from Odoo. You can install the template
before or after the installation of this module.

The template for package label is in the file "init_data.txt".
To load this template you have to print the file (I mean click on print).

Explanation:
This file use the language ZPL (by Zebra).
It contains two requests (between ^XA and ^XZ).
The first request ~DGR will create the logo ALCYON.GRF in the printer.
The second request ^DFE will create the template FORMAT.ZPL for package labels.

Credits
=======

Contributors
------------

* Jacques-Etienne Baudoux <je@bcim.be>
* Sylvain Van Hoof <sylvain@okia.be>
