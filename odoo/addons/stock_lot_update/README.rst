.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

================
Stock Lot Update
================

Allow to modify the product associated to a lot in case of error at encoding.
This also modifies all other tables where the lot and product is referenced in
order to set the new product.

Installation
============

There is no specific installation procedure for this module.

Configuration
=============

/

Usage
=====

Create an incoming shipment and add a line with product1 and lot. Make the
reception and optionaly move or use the product. Go on the lot and change the
reference to product2.

If the product need a lot this module will force
the user to set a lot in the update quantity on hand wizard.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/119/8.0

For further information, please visit:

* https://www.odoo.com/forum/help-1

Known issues / Roadmap
======================

All the references of products are searched based on foreign keys. It could
happen that some tables could not be found this way because there is no link to
the lot.

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
