# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Sale Stock Restocking Fee Invoicing Additional Product",
    "description": """
        Remove additional product from restocking fees""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "depends": [
        # fmt: off
        # Custom
        "alc_additional_product_stock",
        # OCA
        "sale_stock_restocking_fee_invoicing",
        # fmt: on
    ],
    "data": [],
    "demo": [],
    "installable": True,
}
