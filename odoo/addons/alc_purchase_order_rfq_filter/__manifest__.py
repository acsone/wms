# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Purchase Order Rfq Filter",
    "description": """
        This addon automatically apply RFQs filter on PO tree given by
        Requests For Quotation menu item""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # Others
        "purchase",
    ],
    "data": ["views/purchase_order_views.xml"],
    "demo": [],
}
