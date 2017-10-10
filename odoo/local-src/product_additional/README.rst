.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==================
Product Additional
==================

This module adds Alcyon specific fields and logic for product additional.

There are two type of additional product:
- The promotional product (define on the supplier info): For a specific quantity you offer the same product free
- The additional product (define on the product): You link a product to his additional product

The promotional product will be add when you confirm the sale order.
If a product need a promotional product, the module will create a new will without price.

The additional product will be add only when the picking is reserved (stock moves and pack operation).
The quantity of additional product is compute with the "real" reserved quantity for the main product (see example bellow).

Promotional product example:
* On supplier info, create (or modify) a line and add a promotional product (ratio 2/1) (the ratio 2/1 means that if you sold 2 products you give 1 product)
* Create a sale order and add the main product
* Confirm the sale order

Additional product example:
You have 100 units of main products and 15 units of additional product

* Set the additional product on your main product with a ratio of 2/1
* Create and confirm a sale order with this product (quantity 40)
* When you will reserve quantity on the picking, the module will try to take 20 units of additional product.
But you have only 15 units in stock. In this case, the module will only append 15 units of additional product in the pack operation

Credits
=======

Contributors
------------

* Julien Coux <julien.coux@camptocamp.com>
* Sylvain Van Hoof <sylvain@okia.be>
