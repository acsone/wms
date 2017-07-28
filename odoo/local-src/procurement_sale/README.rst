.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

================
procurement_sale
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

There is no specific installation procedure for this module.

Configuration
=============

N/A

Usage
=====

N/A

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/119/8.0

For further information, please visit:

* https://www.odoo.com/forum/help-1

Known issues / Roadmap
======================

* N/A

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/<project name>/issues>`_.
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
