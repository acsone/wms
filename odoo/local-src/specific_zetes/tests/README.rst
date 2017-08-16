=========
Full test
=========

Introduction
============

This test will execute a full scenario for a picker.
From the sign in to the printsing of labels.
Please read following explanation to understand this test

Set up
======

- A picker with the operator code 99
- Three products:
    - Product 1: "Test medoc 1" with a stock of 100 units in the lot 0000001 at the location GAE210
    - Product 2: "Test medoc 2" with a stock of 10 units in the lot 000001 at the location GAD515 (we will simulate an out of stock - only 6 units)
    - Product 2: "Test medoc 3" with a stock of 120 units in two lots 0000001 (20 units) and 0000002 (100 units) at the location GAI110
- A customer "Mr. Docteur Test" who accepts back order
- An open delivery round "TOUR/20170101/01" for the day
- A validated picking with the following configuration:
    - Line 1 with product 1 and a quantity of 10
    - Line 2 with product 2 and a quantity of 10
    - Line 3 with product 3 and a quantity of 50
- Two printser (a Zebra and one Toshiba)

Scenario
========

1. The user will log in (REQU_/RESP_USERCONTEXT)
2. Zetes requests all picking zones (REQU_/RESP_REFDATA)
3. Zetes requests a picking and starts the picking (REQU_/RESP_ASSIGNMENT + RESU_ASSIGNMENT)
4. Zetes requests all picking lines for this picking (REQU_/RESP_ITEMPICK)
5. The picker picks 10 items (REQU_/RESP_CATCHWEIGHT + RESU_CATCHWEIGHT)
6. The picker validates the picking line and goes to the next picking line (ITEMPICK)
7. The picker must takes 10 units of product 2 but there are only 6 units in the stock => Out of stock (REQU_/RESP_CATCHWEIGHT + RESU_CATCHWEIGHT)
8. The picker validates the picking line and goes to the next picking line (RESU_ITEMPICK)
9. The picker takes 20 units of product 3 in the first lot. Now, this lot is empty. The picker will asks for other lots (REQU_/RESP_LOCATION)
   Next, he changes the lot and takes 30 units in the second lot of product 3. (REQU_/RESP_CATCHWEIGHT + RESU_CATCHWEIGHT)
10. The picking is now finished. Zetes changes the picking's state (RESU_ASSIGNMENT)
11. The picker goes to to the packing area and prints labels (REQU_/RESP_PRINT)
12. Zetes asks the label code to check the package and validate the picking (RESU_ASSIGNMENT)
13. The picking is now completely finish. Zetes asks for the next picking (REQU_/RESP_ASSIGNMENT)

===============
Exceptions test
===============

Introduction
============

Test the case when the voice (the hardware) fail and reboot.
This test will not execute a complete scenario. We just want to check what appends when the system crashes.

Set up
======
- A picker with the operator code 99
- Two products:
    - Product 1: "Test medoc 1" with a stock of 100 units in the lot 0000001 at the location GAE210
    - Product 2: "Test medoc 2" with a stock of 10 units in the lot 000001 at the location GAD515
- A customer "Mr. Docteur Test" who accepts back order
- An open delivery round "TOUR/20170101/01" for the day
- A validated picking with the following configuration:
    - Line 1 with product 1 and a quantity of 10
    - Line 2 with product 2 and a quantity of 10

Scenario
========
1. The picker user starts a picking
2. The picker picks the first line
3. The voice crashes and reboot
4. The picker continues the same picking

=================
Interruption test
=================

Introduction
============

Test the case when the picker stop a picking.
A picker cannot stop a picking until he finish an item picks.
This test will not execute a complete scenario.

Set up
======
- A picker with the operator code 99
- An another picker with the operator code 98
- Two products:
    - Product 1: "Test medoc 1" with a stock of 100 unit in the lot 0000001 at the location GAE210
    - Product 2: "Test medoc 2" with a stock of 10 unit in the lot 000001 at the location GAD515
- A customer "Mr. Docteur Test" who accepts back order
- An open delivery round "TOUR/20170101/01" for the day
- A validated picking with the following configuration:
    - Line 1 with product 1 and a quantity of 10
    - Line 2 with product 2 and a quantity of 10
- A printser for passport

Scenario
========
1. The picker starts a picking
2. The picker picks the first line
3. The picker stops the picking
4. A new picker takes this picking
