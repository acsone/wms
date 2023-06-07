# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc label printing base",
    "summary": """
        Code foundation needed to print labels and package labels
        """,
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "depends": ["alc_printing_base", "stock"],
    "data": [
        "security/ir.model.access.csv",
        "wizards/print_label.xml",
        "views/res_partner_views.xml",
        "views/stock_picking_views.xml",
    ],
    "demo": [],
    "installable": True,
}
