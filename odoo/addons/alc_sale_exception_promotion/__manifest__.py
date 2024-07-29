# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Sale Exception Promotion",
    "description": """
        Alcyon specific sale exceptions for promotion""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # fmt: off
        # Custom
        "alc_sale_exception_settings",
        "alc_supplier_promotion",
        # fmt: on
    ],
    "data": ["data/exception_rule.xml"],
    "pre_init_hook": "pre_init_hook",
}
