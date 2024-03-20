=======================================
Alc Stock Picking Put In Pack Type None
=======================================

This module allows to allow to use package types with no carrier integration in picking flows.

Context:

    In internal pickings, even if a carrier is set (like GLS), we want to add 
    the boxes (that have delivery_type == "none") but they won't be available
    as the delivery_type is set to "gls" and there is a filter in the put in pack wizard.

Configuration
=============

To configure this module, you need to:

#. Go to Inventory > Picking Types
#. Go to Package section and check both boxes 'Delivery package type on put in pack'
   and 'Delivery package type none on put in pack.
