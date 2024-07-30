# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Sale Exception Product Category",
    "description": """
        Alcyon specific sale exceptions for product availability""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # Custom
        "alc_partner_type",
        "alc_product_pharmacy",
        "alc_sale_channel",
        "alc_sale_exception",
        "alc_sale_exception_settings",
    ],
    "data": ["data/exception_rule.xml"],
    "pre_init_hook": "pre_init_hook",
}
