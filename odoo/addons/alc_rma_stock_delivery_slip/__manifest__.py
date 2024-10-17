# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Rma Stock Delivery Slip",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # Third-party
        "rma",
        "rma_procurement_customer",
        # Alcyon/Stock
        "alc_stock_delivery_slip",
    ],
    "data": ["views/rma_operation.xml"],
    "demo": [],
}
