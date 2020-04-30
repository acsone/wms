.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===============
Specific Report
===============

This module add some report for Alcyon:
- Delivery round
- Delivery slip
- Invoice (this report contains line to help to fold the paper)
- Purchase Order
- Passport report
- Pharmacist supplier email

The module will add a serial number on stock.move
This serial number is only used on the delivery slip.

Pharmacist supplier email
=========================

An email is sent to a pharmacist containing a sale order report of only
human drugs that are part of the sale order.

This applies only for sales having at least one line with human drug.

Pharmacist is to be set on partner.pharmacist_id field.

Pharmacist email context
----------------------

Human drugs cannot be sold by Alcyon, but they manage only the delivery,
thus the sale order report is sent by email to the supplier directly.

The supplier invoice directly Alcyon's customer and then send the
packages to Alcyon. And finally Alcyon transfer the package to the
customer.

Sale orders can have a mix of Human drugs and other products.

Credits
=======

Contributors
------------

* Sylvain Van Hoof <sylvain@okia.be>
* Yannick Vaucher <yannick.vaucher@camptocamp.com>
