.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

================
Specific Zelapro
================

This specific module add several export for Zelapro:
- Cadancier (header and details)
- Contacs
- Lot moves
- Lots
- Products
- Promotions
- Stock moves
- Supplier


Installation
============

You will need to configure the "Go Live" date.
This date CANNOT be set directly in Odoo (in readonly).
To set the "Go Live" date, please execute the following query the day of Go Live:
INSERT INTO ir_config_parameter VALUES (DEFAULT, 1, NOW(), to_char(NOW(), 'YYYY-MM-DD'), 1, 'zelapro.date_go_live', NOW());

Configuration
=============

You need to configure the operator ID on each use to be able to use Zetes.

Credits
=======

Contributors
------------

* Sylvain Van Hoof <sylvain@okia.be>
