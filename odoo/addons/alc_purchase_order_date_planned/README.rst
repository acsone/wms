.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

================
Alc Purchase Order Date Planned
================

By taking into account both supplier delay and public holidays, this addon
improves the accuracy of the calculation for the date planned in purchase orders.


How to test?
------

- Choose a supplier and specify their Delivery lead time.
- The delay in the supplier's pricelists should update automatically when the
  Delivery lead time is changed.
- When adding a new line to a purchase order, the system will search for a
  supplier pricelist that matches the product and use the delay to calculate
  the planned date for the new line (order date + delay).
- If no pricelist is found, the system will use the Delivery lead time set for
  the supplier.
- The system will take into account public holidays when calculating the date
  planned for a line.
- Check the hr_holidays_public documentation to configure public holidays.
- The order date planned will be updated to the nearest date planned of all
  order lines.
- If the order date planned is updated at any point, it will override the
  computed value for all lines.