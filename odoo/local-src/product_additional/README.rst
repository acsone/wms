.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==================
Product Additional
==================

Manage free additional products in sales and in purchases.

There are two types of additional product: promotional (only for sales) and accessory.


The promotional free product (only for sales)
---------------------------------------------
It is defined on the supplier info. For a specific quantity you offer a product
for free (e.g. 3+1).

The promotional product is added in the sales order at confirmation just before
processing the generation of stock moves for delivery.

That free promotional product is added in the sales order with a price of 0.

In case of sales order cancellation, the promotional product is removed from
the sales order when it is reset to draft.


The accessory free product
--------------------------
It is defined on the product. Is is an other product that is offered when the
main product is sold. (e.g. buy 3 productA and get a free productB).

A) For sales
------------

The accessory product is managed at pack operation. This ensures that you
deliver the quantity of accessories based on the delivered quantity of the
main product.
This ensures that you never deliver an accessory when the main product is not
available.

Technical note: The algorithm looks at the total quantity of the main product
in the created pack operation (could be computed from the aggregation of
multiple stock moves). Then it creates an additional stock move for the
accessory product and reserve it in order to create the corresponding pack
operation for the accessory product. When the main product's pack operation is
deleted, the accessory related move is also cancelled and so its pack
operation is also deleted.

B) For purchase
---------------

Additional products are not automatically computed. The user need to
click on the button "Compute additional products" on the purchase order.
This method will delete all existing additional lines and loop on each
order lines to compute if we need to create a line.

Credits
=======

Contributors
------------
* Jacques-Etienne Baudoux <je@bcim.be>
* Sylvain Van Hoof <sylvain@okia.be>
* Julien Coux <julien.coux@camptocamp.com>
