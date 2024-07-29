# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Product Supplierinfo Check",
    "description": """
        This addon add checks for supplierinfo creation""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # fmt: off
        # Custom
        "alc_supplier_promotion",
        # fmt: on
    ],
    "data": ["views/res_config_settings.xml"],
    "demo": [],
}
