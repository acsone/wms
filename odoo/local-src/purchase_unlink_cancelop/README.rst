.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

========================
Purchase Unlink Cancelop
========================

In standard, when a PO line is deleted, the procurement is set in exception.
However, any quantity in a procurement in exception is taken into account in
the next computation of the orderpoint.
This means that if you decide to not order a product for whatever reason and
delete the PO line, then the product won't come in the next run of the
scheduler unless you cancel manually the related procurement order that has
been put in exception.

With this module, if the procurement is related to an orderpoint, we cancel it
instead of putting it in exception.

This will allow next run of the scheduler to compute a new procurement and
create a new PO line.

Credits
=======

Contributors
------------

* Jacques-Etienne Baudoux <je@bcim.be>
