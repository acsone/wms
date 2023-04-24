.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

======================
ALC RECEPTION PHARMACY
======================

Allows to receive products from the Souverain's pharmacy and ship them to the
customer with an existing shipping if there's already one.

CONFIG
------

* Add the group "Manage Multiple Warehouses" to your user
* Allow group shipping on the warehouse
  (*Inventory - Configuration - Warehouses - Technical Information*)

USAGE
-----
An SO doesn't set the carrier on the shipping automatically even if a default
carrier is set on the customer so you need to set the carrier 'Alcyon Shipping'
on the either through the wizard on the SO or on the delivery if you want it
to be a candidate in grouping for the same partner.