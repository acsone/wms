.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

================
Procurement Sale
================

Ensure that the stock reservation respects sale order confirmation date.
The stock reservation of pickings analyse the stock on hands minus all
deliveries still to process of previous sale orders.
When a sale order is confirmed, the stock is not reserved. This allows you to
move internally your stock between locations.
When a reservation is performed, only available quantity according to you
priority is reserved. This allows you to make deliveries in any order without
having to reserve the stock related to previous sales orders.

If the sale order is canceled and then reconfirmed, we keep the first confirmation
date to ensure customer do not lost his priority after sale order adaptation.

You are also able to set a priority on a rule selectable on the sale order.
This allows to manage the priority of the procurement order from the sale order
line and manage reservation priorities.

In standard, reservation is performed by the scheduler according to the planned
date. This module ensures that the first buyer will be the first served (but
not especially first delivered) whatever the planned date is.

With procurement_jit, the reservation is performed as soon as a sale order is
performed. However, sales orders performed while stock was not available are
never reserved (so only new buyers are served). And having stock automatically
reserved prevents to move stock inside the warehouse.

Installation
============

You need to ensure you don't have procurement_jit installed.

Credits
=======

Contributors
------------

* Jacques-Etienne Baudoux <je@bcim.be>
