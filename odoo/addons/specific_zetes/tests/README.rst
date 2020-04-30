=========
Full test
=========

Introduction
============

This test will execute a full scenario for a picker.
From the sign in to the printing of labels.
Please read following explanation to understand this test

Set up
======

- A picker with the operator code 99
- Three products:
    - Product 1: "Test medoc 1" with a stock of 100 units in the lot 0000001 at the location GD80B1
    - Product 2: "Test medoc 2" with a stock of 10 units in the lot 000001 at the location GD80B2 (we will simulate an out of stock - only 6 units)
    - Product 2: "Test medoc 3" with a stock of 120 units in two lots 0000001 (20 units) and 0000002 (100 units) at the location GD80E8
- A customer "Mr. Docteur Test" who accepts back order
- An open delivery round "TOUR/20170101/01" for the day
- A validated picking with the following configuration:
    - Line 1 with "product 1" and a quantity of 10
    - Line 2 with "product 2" and a quantity of 10
    - Line 3 with "product 3" and a quantity of 50
- Two printer (a Zebra and one Toshiba)

Scenario
========

1. The user will log in (REQU_/RESP_USERCONTEXT)
2. Zetes requests all picking zones (REQU_/RESP_REFDATA)
3. Zetes requests a picking and start the picking (REQU_/RESP_ASSIGNMENT + RESU_ASSIGNMENT)
4. Zetes requests all picking lines for this picking (REQU_/RESP_ITEMPICK)
5. The picker picks 10 items (REQU_/RESP_CATCHWEIGHT + RESU_CATCHWEIGHT)
6. The picker validates the picking line and goes to the next picking line (ITEMPICK)
7. The picker takes 10 units of "product 2" but there are only 6 units => Out of stock (REQU_/RESP_CATCHWEIGHT + RESU_CATCHWEIGHT)
8. The picker validates the picking line and goes to the next picking line (RESU_ITEMPICK)
9. The picker takes 20 units of "product 3" in the first lot. Now, this lot is empty. The picker will ask for other lots (REQU_/RESP_LOCATION)
   Next, he changes the lot and takes 30 units in the second lot of "product 3". (REQU_/RESP_CATCHWEIGHT + RESU_CATCHWEIGHT)
10. The picking is now finished. Zetes changes the picking's state (RESU_ASSIGNMENT)
11. The picker goes to the packing area and prints labels (REQU_/RESP_PRINT)
12. Zetes asks the label code to check the package and validates the picking (RESU_ASSIGNMENT)
13. The picking is now completely finished. Zetes asks for the next picking (REQU_/RESP_ASSIGNMENT)
  A picking will be found because the backorder will be in the delivery round(ALCYN-2130)

===============
Exceptions test
===============

Introduction
============

Test the case when the voice (the hardware) fails and reboots.
This test will not execute a complete scenario. We just want to check what appends when the system crashes.

Set up
======
- A picker with the operator code 99
- Two products:
    - Product 1: "Test medoc 1" with a stock of 100 units in the lot 0000001 at the location GD80B1
    - Product 2: "Test medoc 2" with a stock of 10 units in the lot 000001 at the location GD80B2
- A customer "Mr. Docteur Test" who accepts back order
- An open delivery round "TOUR/20170101/01" for the day
- A validated picking with the following configuration:
    - Line 1 with "product 1" and a quantity of 10
    - Line 2 with "product 2" and a quantity of 10

Scenario
========
1. The picker user starts a picking
2. The picker picks the first line
3. The voice crashes and reboots
4. The picker continues the same picking

=================
Interruption test
=================

Introduction
============

Test the case when the picker stops a picking.
A picker cannot stop a picking before he finished an item pick.
This test will not execute a complete scenario.

Set up
======
- A picker with the operator code 99
- An another picker with the operator code 98
- Two products:
    - Product 1: "Test medoc 1" with a stock of 100 units in the lot 0000001 at the location GD80B1
    - Product 2: "Test medoc 2" with a stock of 10 units in the lot 000001 at the location GD80B2
- A customer "Mr. Docteur Test" who accepts back order
- An open delivery round "TOUR/20170101/01" for the day
- A validated picking with the following configuration:
    - Line 1 with "product 1" and a quantity of 10
    - Line 2 with "product 2" and a quantity of 10
- A printer for passport

Scenario
========
1. The picker starts a picking
2. The picker picks the first line
3. The picker stops the picking
4. A new picker takes this picking

=================
Full test parking
=================

Introduction
============

This test will execute a full scenario for a picker in parking.
Please read following explanation to understand this test

Set up
======

- A picker with the operator code 99
- Two products:
    - Product 1: "Test medoc 1" with 100 units in parking PARKING001
    - Product 2: "Test medoc 2" with 20 units in parking PARKING001

Scenario
========

1. The user will log in (REQU_/RESP_USERCONTEXT)
2. Zetes requests all picking zones (REQU_/RESP_REFDATA)
3. Zetes requests a picking and start the picking (REQU_/RESP_ASSIGNMENT + RESU_ASSIGNMENT)
4. Zetes requests all picking lines for this picking (REQU_/RESP_ITEMMOVE)
5. The picker unload 5 items of product 2 (RESU_CATCHWEIGHT)
6. The picker picks 75 items (REQU_/RESP_CATCHWEIGHT + RESU_CATCHWEIGHT) and validates the picking line (RESU_ITEMPICK)
7. The picker goes to the reserve (for the remaining products) (REQU_/RESP_LOCATION)
8. The picker put 25 items of product 1 in the reserve and goes to the next picking line (REQU_/RESP_CATCHWEIGHT) (RESU_ITEMMOVE)
9. The picker takes 15 units of product 2 (REQU_/RESP_CATCHWEIGHT + RESU_CATCHWEIGHT) and validates the picking line (RESU_ITEMPICK)
10. The picking is now completely finished. Zetes asks for the next picking (REQU_/RESP_ASSIGNMENT)

=================
Full test reserve
=================

Introduction
============

This test will execute a full scenario for a picker in reserve.
Please read following explanation to understand this test.

Set up
======

- A picker with the operator code 99
- Two products:
    - Product 1: "Test medoc 1" with 20 units in the reserve
    - Product 2: "Test medoc 2" with 100 units in the reserve

Scenario
========

1. The user will log in (REQU_/RESP_USERCONTEXT)
2. Zetes requests all picking zones (REQU_/RESP_REFDATA)
3. Zetes requests a picking and start the picking for product 1 (REQU_/RESP_ASSIGNMENT + RESU_ASSIGNMENT)
4. Zetes requests a picking line (REQU_/RESP_ITEMMOVE)
5. The picker takes 20 units of product 1 and put it in the stock (RESU_CATCHWEIGHT) (RESU_ITEMMOVE)
6. Zetes requests a picking and start the picking for product 2 (REQU_/RESP_ASSIGNMENT + RESU_ASSIGNMENT)
7. Zetes requests a picking line (REQU_/RESP_ITEMMOVE)
8. The picker takes 80 units of product 1 (the bin is full) and put it in the stock (RESU_CATCHWEIGHT) (RESU_ITEMMOVE)
