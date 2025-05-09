# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Product Abc Classification Link",
    "summary": """Links the "abc_storage"(stock_storage_type_putaway_abc) parameter of product templates to the "abc_classification_product_level_ids" (product_abc_classification)""",
    "version": "16.0.1.0.2",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # Odoo Community
        "product",
        # Third-party
        "product_abc_classification",
        "stock_storage_type_putaway_abc",
    ],
    "data": [],
    "demo": [],
}
