==============================================
Alc Sale Loyalty Year End Rebate Applicability
==============================================

Manage retroactive application of a program when adding a new beneficiary

Purpose
=======

When a partner is modified, we check if the partner is a beneficiary of a year_end_rebate program.
* If it's the case and no Loyalty Card for this program exists for this partner. We search for all sale orders passed since the date of the signature of the alcyonaire contract and we retroactively apply the program to all these sale orders.
* If it's no more the case and a Loyalty Card for an active program exists for this partner, we remove the Loyalty Card and all the points associated to this program.

