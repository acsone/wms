# Copyright 2018 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Cash on delivery",
    "version": "16.0.1.0.0",
    "author": "BCIM,ACSONE SA/NV",
    "category": "Stock Management",
    "depends": [
        # Others
        "account",
        "sale_stock",
    ],
    "data": ["views/account_payment_term_views.xml", "views/stock_picking_views.xml"],
    "installable": True,
    "license": "AGPL-3",
}
