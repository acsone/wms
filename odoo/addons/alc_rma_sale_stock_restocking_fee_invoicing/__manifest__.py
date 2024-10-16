# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Rma Sale Stock Restocking Fee Invoicing",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # Third-party
        "rma_sale",
        "rma_sale_reason",
        "sale_stock_restocking_fee_invoicing",
    ],
    "data": ["views/rma_reason.xml"],
    "demo": [],
}
