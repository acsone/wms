.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=======================
Specific Shipping Costs
=======================

This module adds Alcyon specific workflow for calculating the shipping costs for a customer.
It can replace the default one of the Delivery Methods.
To enable this computation of the shipping costs over the standard one use the checkbox
'Alcyon specific cost' on the Delivery Methods form.


Configuration
-------------

A customer is exempted of shipping fees, if the checkbox Helps With Fees is not checked on his configuration page.

Above a minimum amount ordered for a specific period the customer does not have to pay shipping fees.
The fixed price and the amount necessary to have a free delivery are the one declared on the Delivery Method.


Notes
-----
On the sale order the desired delivery method is set depending on the customer or manually.

The round instance can have more than one type of delivery method declared in the sale order that it has
to manage.


When and how are the shipping cost computed
--------------------------------------------

The shipping costs are calculated when a delivery round is set to done.

To find out if a customer needs to pay shipping costs, the system :
    * Sums all the customer new sale orders that have not yet been used for this calculation,
      but only the sale order who have the same delivery method.
      (Even the one that are not in this round yet)
    * If the amount is below the limit to get free shipping a new shipping fee line is added
      on the last sale order passed by the customer.

A sale order is only used once in the calculation of the shipping fee.


Contributors
------------

* Thierry Ducrest <thierry.ducrest@camptocamp.com>
* Julien Coux <julien.coux@camptocamp.com>
