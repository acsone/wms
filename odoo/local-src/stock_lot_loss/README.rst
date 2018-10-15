.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==============
Stock Lot Loss
==============

When a sale is confirmed, Odoo will reserve the quantity to pick.
It means that Odoo will reserve a specific quantity for a specific lot (if the product use tracking with lot).

During the picking, the picker need to be able to indicate that the lot is empty (in the stock) even if this lot
is not empty in Odoo.
In this case, we need to unreserve the remaining quantity for the current operation (pack.operation) and look for an another lot for this
product.

Credits
=======

Contributors
------------

* Jacques-Etienne Baudoux <je@bcim.be>
* Sylvain Van Hoof <sylvain@okia.be>
