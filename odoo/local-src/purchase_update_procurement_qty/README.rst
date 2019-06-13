.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===============================
Purchase Update Procurement Qty
===============================

In standard when the product qty on a purchase line is decreased and there are
related procurement orders, the procurements keep running forever because the
qty on the procurement is still the original qty and this will never be
fullfilled (since we purchased fewer products).

This module attempts to remedy this.

Credits
=======

Contributors
------------

* Alexandre Fayolle <alexandre.fayolle@camptocamp.com>
