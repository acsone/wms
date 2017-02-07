.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==============
Specific Stock
==============

This module adds Alcyon specific fields and logic for stock.

* Allow to manage expired times on product category
* Add a required constraint on life date of "serial numbers / lots"
* Allow to set life date directly on picking transfer wizard
* Create a cron to archive lot
* Assign a unique (N-2/N+2) checksum on lot
* Check if the removal date is not expired when we receive a lot

Credits
=======

Contributors
------------

* Julien Coux <julien.coux@camptocamp.com>
* Jacques-Etienne Baudoux <je@bcim.be>
