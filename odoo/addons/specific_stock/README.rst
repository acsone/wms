.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==============
Specific Stock
==============

This module adds Alcyon specific fields and logic for stock.

* Allow to manage expired times on product category
* Add a required constraint on expiration date of "serial numbers / lots"
* Create a cron to archive lot
* Assign a unique (N-2/N+2) checksum on lot
* Check if the removal date is not expired when we receive a lot
* Indicate in reception wizard if operation is related to a product in backorder
* Create a cron to create automatically a daily inventory according some rules
* Move the button "Put in Pack" in the form's header
* Add a reception wizard for the dropshipping of human drug packs


Credits
=======

Contributors
------------

* Julien Coux <julien.coux@camptocamp.com>
* Jacques-Etienne Baudoux <je@bcim.be>
