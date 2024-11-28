# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Test MTO product orderpoints flow",
    "summary": """
       Test .""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # Third-party
        "stock_orderpoint_default_location",
        # Alcyon
        "alc_sale_mto_check_procurements",
        "alc_stock_orderpoint_product_mto",
        "alc_stock_release_channel_assign_blocking_unavailable_product_mto",
        # Alcyon/Stock Management
        "alc_stock_orderpoint_product",
    ],
}
