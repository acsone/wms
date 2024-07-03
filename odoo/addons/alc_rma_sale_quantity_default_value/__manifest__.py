# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Rma Sale Quantity Default Value",
    "description": """
    This addon sets 0 as the default value for the quantity to return using the RMA wizard.
    This change simplifies RMA creation for large orders.
    """,
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": ["rma_sale"],
    "data": [
        "wizards/sale_order_rma_wizard.xml",
    ],
    "demo": [],
}
