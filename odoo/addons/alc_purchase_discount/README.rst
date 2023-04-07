.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

================
Alc Purchase Order Discount
================

Based on oca module `purchase_discount`, this module add two fields to purchase
order lines to compute the discount.

How to test?
------------

- Set the `supplier discount` on the supplier.
- Set the the discount on the supplier pricelist
- When you add a new line to a purchase order, if it matches a supplier pricelist,
  the pricelist discount will be set in the `promotion supplier` field.
- The `global discount` will be filled with the supplier discount.
- The discount field from the oca module will be computed as:
  discount = 100 - ((100 - `discount global`) * (100 - `promotion supplier`) / 100)
- The discount field was hidden to simplify the view.
