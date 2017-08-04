=========
Full test
=========

Introduction
============

This test will execute a full scenario for a pickeur.
From the sign in to the printing of labels.
Please read following explanation to understand this test

Set up
======

- A picker with the operator code 99
- Three products:
    - Product 1: "Test medoc 1" with a stock of 100 unit in the lot 0000001 with the location GAE210
    - Product 2: "Test medoc 2" with a stock of 10 unit in the lot 000001 with the location GAD515 (we will simulate an out of stock - only 6 units)
    - Product 2: "Test medoc 3" with a stock of 120 unit in two lots 0000001 (20 units) and 0000002 (100 units) with the location GAI110
- A customer "Mr. Docteur Test" who accepts back order
- An open delivery round "TOUR/20170101/01" for the day
- A validated picking with the following configuration:
    - Line 1 with product 1 and a quantity of 10
    - Line 2 with product 2 and a quantity of 10
    - Line 3 with product 3 and a quantity of 50
- Two printer (a Zebra and one Toshiba)

Scenario
========

1. The user will log in (REQU_/RESP_USERCONTEXT)
2. Zetes request all picking zones (REQU_/RESP_REFDATA)
3. Zetes request a picking and start the picking (REQU_/RESP_ASSIGNMENT + RESU_ASSIGNMENT)
4. Zetes request all picking lines for this picking (REQU_/RESP_ITEMPICK)
5. The picker pick 10 items (REQU_/RESP_CATCHWEIGHT + RESU_CATCHWEIGHT)
6. The picker valid the picking line and go the next picking line (ITEMPICK)
7. The picker should take 10 units of product 2 but there are only 6 unit => Out of stock (REQU_/RESP_CATCHWEIGHT + RESU_CATCHWEIGHT)
8. The picker valid the picking line and go the next picking line (RESU_ITEMPICK)
9. The picker take 20 units of product 3 in the first lot. Now, this lot is empty. The picker will ask for other lots (REQU_/RESP_LOCATION)
   Next, he change the lot and take 30 units in the second lot of product 3. (REQU_/RESP_CATCHWEIGHT + RESU_CATCHWEIGHT)
10. The picking is now finish. Zetes change the state of the picking (RESU_ASSIGNMENT)
11. The picker go to the packing area and print labels (REQU_/RESP_PRINT)
12. Zetes ask the label code to check the package and validate the picking (RESU_ASSIGNMENT)
13. The picking is now completely finish. Zetes ask for the next picking (REQU_/RESP_ASSIGNMENT)

===============
Exceptions test
===============

Introduction
============

Test the case when the voice (the hardware) fail and reboot.
This test will not execute a complete scenario. We just want to check what appends when the system crash.

Set up
======
- A picker with the operator code 99
- Two products:
    - Product 1: "Test medoc 1" with a stock of 100 unit in the lot 0000001 with the location GAE210
    - Product 2: "Test medoc 2" with a stock of 10 unit in the lot 000001 with the location GAD515
- A customer "Mr. Docteur Test" who accepts back order
- An open delivery round "TOUR/20170101/01" for the day
- A validated picking with the following configuration:
    - Line 1 with product 1 and a quantity of 10
    - Line 2 with product 2 and a quantity of 10

Scenario
========
1. The picker user start a picking
2. The picker pick the first line
3. The voice crash and reboot
4. The continue the same picking

=================
Interruption test
=================

Introduction
============

Test the case when the picker stop a picking.
A picker cannot stop a picking until he finish an item pick.
This test will not execute a complete scenario.

Set up
======
- A picker with the operator code 99
- An another picker with the operator code 98
- Two products:
    - Product 1: "Test medoc 1" with a stock of 100 unit in the lot 0000001 with the location GAE210
    - Product 2: "Test medoc 2" with a stock of 10 unit in the lot 000001 with the location GAD515
- A customer "Mr. Docteur Test" who accepts back order
- An open delivery round "TOUR/20170101/01" for the day
- A validated picking with the following configuration:
    - Line 1 with product 1 and a quantity of 10
    - Line 2 with product 2 and a quantity of 10
- A printer for passport

Scenario
========
1. The picker start a picking
2. The picker pick the first line
3. The picker stop the picking
4. A new picker take this picking
