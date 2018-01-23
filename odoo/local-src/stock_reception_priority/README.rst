.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

========================
Stock Reception Priority
========================

Compute the priority (rank) used to sort the incoming shipments.

The rank is computed based on customer deliveries waiting for goods.

Formula: Rank = qty_backorder * 1000 + qty_outofstock

Where:
- qty_backorder = Quantity of deliveries part of a delivery round waiting for
  availability. For each product of the reception order, we count the customers
  (delivery address) waiting for the goods and we sum those quantities.

  Note that a delivery is only part of a delivery round if it can be partially
  (or entirely) delivered. If nothing is available, then the delivery is not
  linked to a delivery round.
  So we give here highest importance to deliveries partially available.

- qty_outofstock = Quantity of products where the available stock is negative (< 0).
  The available quantity is the quantity on hands minus the quantity to deliver.
  So we give here second importance to deliveries not available.

The rank is computed when the GRN is associated to the incoming shipment. A
cron job recomputes the rank regularly.


Installation
============

There is no specific installation procedure for this module.

Configuration
=============

/

Usage
=====

/

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/119/8.0

For further information, please visit:

* https://www.odoo.com/forum/help-1

Known issues / Roadmap
======================

/

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/<project>/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and
welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Jacques-Etienne Baudoux <je@bcim.be>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
