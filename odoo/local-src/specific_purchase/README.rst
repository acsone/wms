.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=================
Specific Purchase
=================

This module adds Alcyon specific fields and logic for purchase:
- Add two discounts on purchase order (discount global and discount pricelist)
- Add a supplier discount on the partner form
- Compute the total weight of a purchase order
- On a supplier you can define if it support back order or not
- If the supplier doesn't support "back order" a validated purchase order
will never create a back oder
- A purchase order is automatically validated


Credits
=======

Contributors
------------

* Cyril Gaudin <cyril.gaudin@camptocamp.com>
* Julien Coux <julien.coux@camptocamp.com>
