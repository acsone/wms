.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==========
Stock Unit
==========

Try to reserve quants first by (nearly) complete packaging.  This can be
combined with fifo or fefo removal strategy allowing to bypass that
strategy to first consider a nearly entire packaging because it's practically
more convenient.
Note that this is based on quants typically created at reception. We don't
manage real packages in stock. We only consider that received goods are already
packaged properly and that a quant with a high quantity contains packaged goods.

3 types of packaging are added on the product: pallet, box, shrink-wrap

Installation
============

There is no specific installation procedure for this module.

Configuration
=============

You can define factor for each packaging specifying what is the acceptable
percentage of a package.

You can also define the minimum quantity that acceptable package must have at
least.

Examples
--------
Pallet = 80 units
Box = 10 units

Pallet factor = 0.7
Box factor = 0.8

Quantity to reserve = 70
80*0.7=56 <= 70 -> take preferrably a pallet and remove 24 units

Quantity to reserve = 39
10*0.8=8 -> take 4 boxes and remove 1 unit from 1 box
If min quantity=9: take 3 boxes and take 9 units

Quantity to reserve = 37
10*0.8=8 -> take 3 boxes and take 7 units

Credits
=======

Contributors
------------

* Jacques-Etienne Baudoux <je@bcim.be>
