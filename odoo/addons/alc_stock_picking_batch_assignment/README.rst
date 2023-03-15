===================
Stock Picking Start
===================

This module allows assigning an operator (``user_id``) to all the pickings on the batch.
It also relies on ``alc.stock.picking.start`` and allows the user to start or cancel
all individual pickings using buttons on the batch form view.


Testing
=======

- Create a new batch and add pickings;
- Make sure that the start button is not visible until all pickings are ready to start;
- Start the batch and cancel, verifying that the pickings are started and canceled accordingly;
