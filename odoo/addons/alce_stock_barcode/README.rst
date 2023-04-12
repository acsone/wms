==================
Alce stock barcode
==================

When scanning a location, open a picking with the right picking type. That
picking type is defined on the location or one of the parent.

Usage
=====

* Enable *Storage Locations* in *Settings - Inventory - Warehouse*
* Use barcode interface and scan a location or a picking


Test
----

* Scan a location (internal usage)
* Scan a product
* Validate the picking
* Check the source location is the one you scanned and the destination location
  is given by the Barcode Picking Type set on location or one parent
* If you scanned a picking you can then scan a product or a lot and the
  corresponding operation is incremented. There is also a special barcode
  (C#ALLDONE) which can set all the quantities in one scan.

Credits
=======

Contributors
------------

* Jacques-Etienne Baudoux <je@bcim.be>
* Hughes Damry <hughes.damry@acsone.eu>
