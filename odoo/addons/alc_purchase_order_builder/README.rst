.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=======================
Website purchase review
=======================


This specific module offers a web view to review purchase order.


Installation
============

There is no specific installation procedure for this module.


Tests
=====

- Create a new purchase order with several items, do not confirm it;
- Make sure at least some of the items have defined orderpoints, and some use lots;
- Click on the open PO button in the top button box. This should open the view;
- In the top pannel, set discount and promotion and save. They apply to all PO lines;
- Check navigation between PO lines using the arrows;
- Check the progress bar and the to confirm / confirm badge are correct;
- The values in the left pannel apply to the PO line except for the stock min/max;
- The stock min/max apply to the PO line product's orderpoints (also on product itself);
- Confirm new values and make sure the PO line and orderpoints are updated;
- In the rightmost pannel check the various filters.

Credits
=======

Contributors
------------

* Sylvain Van Hoof <sylvain@okia.be>
