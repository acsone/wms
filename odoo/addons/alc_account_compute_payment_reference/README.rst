=====================================
Alc Account Compute Payment Reference
=====================================

For recompute of payment reference when state change

Purpose
=======

This module add a depends on the method `_compute_payment_reference` in the model `account.payment` to recompute the payment reference when the state change.
We observed that the payment reference is not recomputed when the state change from posted to draft for exemple. Despite a PR into the core, Odoo refused to merge it. 
So we decided to create this module to fix this issue we observed at least into the Alcyon project.