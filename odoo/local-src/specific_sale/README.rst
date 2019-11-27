.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=============
Specific Sale
=============

This module adds Alcyon specific fields and logic for sale order:

* On sale order form view :

  * add onchange to check rule exception without wait the order confirmation
  * add product quantity unavailable (model, view, report)
  * on sub-form view for sale order lines

    * add product quantity unavailable
    * add Lots/Serial Numbers in stock
    * add next expected date for receipt (the receipt of the next purchase order)

* Ability to ship only the available quantity when confirming a sale order:

  * new option on partner to enable the feature
  * when confirming an order, the unavailable qty for an order line will be
    set in the "Qty canceled" field and the "Ordered Qty" field will be updated
    with the available stock qty
  * the created stock move will reflect the updated Ordered Qty (avoiding
    the generation of shipping backorders)


Credits
=======

Contributors
------------

* Cyril Gaudin <cyril.gaudin@camptocamp.com>
* Julien Coux <julien.coux@camptocamp.com>
