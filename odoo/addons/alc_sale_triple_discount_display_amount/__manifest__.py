# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Sale Triple Discount Display Amount",
    "summary": """Glue module between sale_triple_discount and sale_discount_display_amount enabling discount_total field to depend from all 3 discounts.""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # Third-party
        "sale_discount_display_amount",
        "sale_triple_discount",
    ],
    "data": [],
    "demo": [],
}
