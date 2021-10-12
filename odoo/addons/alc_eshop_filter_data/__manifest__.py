# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alcyon e-shop Product Filters",
    "description": """Alcyon e-shop Product Filters""",
    "version": "10.0.1.0.0",
    "depends": [
        "alc_pim",  # filter dependencies
        "shopinvader",  # TODO: use, shopinvader_product_attribute_set replacing
    ],  # TODO: v10 shopinvader_custom_attribute which does not work (prePIM)
    "author": "ACSONE SA/NV",
    "website": "http://www.acsone.eu",
    "license": "AGPL-3",
    "category": "alc",
    "data": ["data/product_filter.xml"],
    "installable": True,
}
