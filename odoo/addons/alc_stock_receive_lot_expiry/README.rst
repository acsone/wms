============================
Alc Stock Receive Lot Expiry
============================

Extends the Alcyon reception wizard to check if the removal date of a product
is expired upon receiving a lot.

If the removal date is expired the line is marked with a red excalmation
triangle after the expiration date.

Test
====

* Proceed as you would do for the alc_stock_receive_lot
* if you enter a date in the past in expiration date you get a red excalmation
  triangle to alert you
