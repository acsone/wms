====================================
Alc Sale Auto Cancel Unavailable Qty
====================================

Automatically cancel unavailable ordered quantity to avoid the generation of backorders

Configuration
=============

To configure this module, you need to:

#. Go to ...

Tests
=====

- On a contact, in the "Sale & Purchase" tab check "Auto-cancel Unavailable Quantity";
- Create a sale order with that partner as client;
- Add a sol with more quantities than are available;
- When confirming the order the quantity should be adjusted to the avalaible quantity,
and the unavailable quantity should be cancelled;
- Check that the moves are created with the adjusted quantities;
- Check there are no backorders.


Changelog
=========
