.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=================
Stock Receive Lot
=================

Add a new reception wizard to more easily encode destination, lot and expiration date.

Also improve the standard lot reception wizard to allow to set expiration date.

Disable standard check that prevent to create a lot at reception.

Tests
=====

- Create a new purchase order with a few different products in some quantity, then confirm it;
- Click *Receive Product* on the PO, then *Receive* on the picking;
- Choose an operation (aka move line): there should be only one per move for a newly created PO;
- After setting the operation, the *Destination Location* should be set automatically;
- Set the expiration date and lot name (if required) and the quantity;
- Click either *Next lot* or *Next Operation* (try both) and check that the move line was updated by clicking on the parent move on the picking screen;
- Do this with products with lot tracking and without. When there are several lot by move line, the move line should be split, otherwise the quantity is simply added;
- Do this with a product with the *Aliments* category or one of it's child categories. On those the lot name should be set automatically after you enter the expiration date.
  If the lot does not exists, it will be created, if yes, it will be reused (Use Create Lots option should be enabled on Operation Type level).

Credits
=======

Contributors
------------

* Jacques-Etienne Baudoux <je@bcim.be> (BCIM)
* Julien Coux <julien.coux@camptocamp.com>
