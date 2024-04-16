.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

========================
Stock Reception Priority
========================

Compute the priority (rank) used to sort the incoming shipments.

The rank is computed based on customer deliveries waiting for goods.

Formula: Rank = count_partners_for_product * 1 000 +
count missing products.


The rank is computed when the GRN is associated to the incoming shipment. A
cron job recomputes the rank regularly.


This addon also adds 2 fields previoulsy used into the rank computation:

- count_planned_partners_waiting_for_reception = Quantity of deliveries waiting for
  availability. For each product of the reception order, we count the customers
  (delivery address) waiting for the goods and we sum those quantities. (
  deliveries into a release_channel)

- count_planned_products_waiting_for_reception = Count of products waiting for
  availability. For each product of the reception order, we count the number
  of products waiting for the goods.(deliveries into a release_channel)

The previous rank computation was based on the following formula:

Rank = ccount_planned_partners_waiting_for_reception * 1 000 000 000 +
count_planned_products_waiting_for_reception 1 000 000 + count_partners_for_product * 1 000 +
count_missing_products


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
