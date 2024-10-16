# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


{
    "name": "Test: Alcyon Pricing",
    "description": """Test Alcyon Pricing:
    Module grouping price functionality.
    Since triple discounts, supplier discounts and other features cannot be fully tested
    without grouping all these dependencies.
    """,
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # Third-party
        "onchange_helper",
        # Alcyon
        "alc_price_cache_exclusive",
        "alc_price_triple_discount_exclusive",
        "alc_pricing_constraints",
        "alc_supplier_promotion",
        # Alcyon/Sales Management
        "alc_pricelist_discount",
    ],
    "application": False,
    "data": [],
    "demo": [],
}
