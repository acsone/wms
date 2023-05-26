.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==========================
Alcyon Pricing Constraints
==========================

This module adds a new menu under sale>product to access pricelist items. It also
introduces some constraints to limit pricelist support:

- Formula based pricelist items are not supported.
- Items with minimal quantity are only supported for product based item.

In addition, this module ignore useless global pricelist items creation, like
a 0 discount..