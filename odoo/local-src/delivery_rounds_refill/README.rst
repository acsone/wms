.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

======================
Delivery rounds refill
======================

Manage arrangement (parking to reserve or bin) and reassortment (reserve to bin).

Reassortment
------------

The reassortment report computes in real-time a priority to perform reassortment.
A priority is computed for each product in stock.
The report shows the first quant of each product to reassort according to fefo/fifo.

The priority is computed following those rules.
For the highest value:
    > 6000: out of stock and part of a launched delivery round
    > 5000: out of stock and part of a delivery round
    > 1000: out of stock based on all confirmed deliveries
    < 1000: out of stock in 2 days based on average deliveries on last 7 days
    = 0   : enough stock
For the lowest value: amount of deliveries (no matter they could be
fulfilled with current stock or not).

Known issues / Roadmap
======================

The report does not take into account quant's owner and multi-company

Credits
=======

Contributors
------------

* Jacques-Etienne Baudoux <je@bcim.be>
