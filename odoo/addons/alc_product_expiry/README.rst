==================
Alc Product Expiry
==================
Currently, the stock_available_to_promise_release mechanism does not take into
account the lot expiration date. An expired lot is included in the promised
quantity and reserved for movements.
This addon exclude expired lots during availability checks

Configuration
=============

To configure this module, you need to:

#. Go to operation types and set the types you want to prohibit expired lot reservation.

Usage
=====

For the types that don't allow expired lot reservation, expired lots will not
be counted in the available stock. An expired lot for a given move is defined
as a lot with a removal date later than its scheduled date.

If for any reason you want to ignore this rule for a given picking, you can
check the box to bypass it. This permission will be propagated in both ways,
from out to pick and from pick to out.

In all cases the lot is checked when validation the picking. This prevent the
case where permission is given before reservation and removed then.
