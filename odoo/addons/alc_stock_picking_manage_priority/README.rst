=====================================
Alc Stock Picking Priority Management
=====================================

This module enables the capability to manage the priority of a stock picking.
The goal is to restrict the users allowed to change the picking priority.

Be aware this restriction only affects the changes done by UI and the **priority
is no more editable if the move priority setting is turned off (default)**.

Config
======

The priority is no more editable if the move priority setting is turned off
(default).

Usage
=====

The manage move priority setting can be reached by:

- Company: *Settings* - *Inventory* - *Operations*
- or *Inventory* - *Configuration* - *Settings* - *Operations*

Once there you can turn on/off "Manage Move Priority".

The priority can be set on picking if:

- The manage move priority setting is turned on
- **and** the user is part of the 'stock move priority manager' group
- **and** the picking is not locked
- **and** the picking state is not 'done' or 'cancel'


