# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Sale Invoicing On Transfer",
    "description": """
        Alcyon: Allows invoice creation on stock picking transfer for sale orders

        Add a flag on picking type to set when we want the invoice to be
        generated at transfer.
        """,
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # Third-party
        "partner_invoicing_mode_at_shipping",
        "partner_invoicing_mode_at_shipping_group_by_partner_by_carrier",
    ],
    "data": ["views/stock_picking_type.xml"],
    "demo": [],
}
