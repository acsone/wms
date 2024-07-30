# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Account Invoice Vendor Bill Autocomplete",
    "version": "16.0.1.0.0",
    "summary": "Restraints the autocomplete of invoice vendor bill id to"
    " old invoices and PO to invoice",
    "author": "ACSONE SA/NV",
    "license": "AGPL-3",
    "category": "Accounting & Finance",
    "depends": [
        # Others
        "purchase",
    ],
    "data": ["views/account_move_views.xml"],
    "installable": True,
}
