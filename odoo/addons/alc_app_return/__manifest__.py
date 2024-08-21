# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Return App",
    "description": """
        Gather all return related modules for Alcyon""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "application": True,
    "depends": [
        # Custom
        "alc_sale_stock_restocking_fee_invoicing_additional_product",
        # OCA
        "stock_picking_return_lot",
    ],
}
