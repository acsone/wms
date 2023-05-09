.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

====================
Pricelist Role Names
====================

Technical module to compute a role name for sale pricelists.
It adds two new fields to the pricelist model (not visible in the UI).

- role_name = "price-" + the pricelist name
- discount_role_name = "discount_" + the role_name


