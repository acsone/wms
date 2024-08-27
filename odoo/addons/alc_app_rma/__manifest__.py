# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc RMA App",
    "description": """
        Gather all rma related modules for Alcyon""",
    "version": "16.0.1.0.2",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "application": True,
    "depends": [
        # OCA
        "product_warranty",
        "rma",
        "rma_lot",
        "rma_reason",
        "rma_sale",
        "rma_sale_lot",
        "rma_sale_reason",
    ],
}
