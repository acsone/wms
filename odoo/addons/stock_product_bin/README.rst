.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=================
Stock Product Bin
=================

Define on the product in which bin it should be stored. You can defined
multiples rules based on different stock location.
The put away strategy is modified to take care of that configuration.

This module allows to assign a location/bin on a product.
This assignment can be occur in the product view or in the wizard "Update quantity on hand".

Installation
============

There is no specific installation procedure for this module.

Configuration
=============

Fill the stock location - bin mapping table on the products.

Usage
=====

Define on a product that if it is moved to WH1/My Stock, it must be stored in
WH1/My Stock/BinA3C.

Define on a product that if it is moved to WH2/Stock Owner1, it must be stored
in WH2/Stock Owner1/BinF4H.

Make a stock move to WH1/My Stock. In the stock operation, the destination must
be the bin you have configured.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/119/8.0

For further information, please visit:

* https://www.odoo.com/forum/help-1

Known issues / Roadmap
======================

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
* Sylvain Van Hoof <svh@sylvainvh.be>

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
