.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=================
Specific Purchase
=================

This module adds Alcyon specific fields and logic for purchase:
- Add two discounts on purchase order (discount global and promotion supplier)
- Add a promotion supplier on the product supplierinfo form (On the partner and purchase, you can allow or not the computation)
- Compute the total weight of a purchase order
- On a supplier you can define if it support back order or not
- If the supplier doesn't support "back order" a validated purchase order
will never create a back oder
- A purchase order is automatically validated
- Add the unique supplier on the product form
- Send an email to the supplier when a purchase order is canceled with the reason
- Add some attributes (like weight, depth, unit_in_box, ...) on the product
- Allow to manager bank holidays (used to compute the scheduled date)

Procurement order
=================

This module contains a cron to generate procurement orders each day.
To avoid to create to much procurement orders, Alcyon manage only a subset of suppliers per day.
The day of management is set on the supplier (field is_manage_day_#WEEKDAY).
When the cron will run, we will only take suppliers with the current current day (monday == 1; sunday == 7).

The user has the possibility to execute this cron manually.
In this case, he can chose to select a specific day (to create procurement orders for the next day for example)
or he can select a specific supplier.

Credits
=======

Contributors
------------

* Sylvain Van Hoof <sylvain@okia.be>
* Julien Coux <julien.coux@camptocamp.com>
